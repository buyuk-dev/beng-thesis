""" 2021 Created by michal@buyuk-dev.com
"""

import sys

import threading
import multiprocessing
from pprint import pformat

import muselsl
import pylsl

from server import configuration
from server.logger import logger

from server import utils


# DO NOT CHANGE THIS FUNCTION, READ DOCSTRING
def Stream_stream_process(address):
    """needs to be a global scope, importable object due to pickling
    done in multiprocessing.
    """
    muselsl.stream(address=address, backend="bleak")


class InletAdapter(pylsl.StreamInlet):
    """Provides easier access to inlet properties."""

    def __init__(self, *args, **kwargs):
        """Initialize inlet."""
        super().__init__(*args, **kwargs)

    def get_sampling_rate(self):
        """Return stream sampling rate."""
        return int(self.info().nominal_srate())

    def get_channels_count(self):
        """Return number of channels in the stream."""
        return self.info().channel_count()

    def get_channels(self):
        """Parse info about channels from xml description."""
        xml = self.info().desc().child("channels").child("channel")
        channels = []
        for _ in range(self.get_channels_count()):
            channels.append(xml.child_value("label"))
            xml = xml.next_sibling()
        return channels

    def __str__(self):
        """Return readable info about connected stream."""
        return pformat(
            {"sampling_rate": self.get_sampling_rate(), "channels": self.get_channels()}
        )


def find_lsl_stream(max_chunklen=30, timeout=30, stream_type="EEG"):
    """Resolve existing LSL stream with EEG data."""
    streams = pylsl.resolve_byprop("type", stream_type, timeout=timeout)
    if len(streams) == 0:
        logger.warning("No active streams have been found.")
        return None

    logger.info(f"Found {len(streams)} active streams.")
    for idx, stream in enumerate(streams):
        logger.info(f"{idx}: {stream}")

    logger.info("Connecting to stream #0.")
    inlet = InletAdapter(streams[0], max_chunklen=max_chunklen)

    logger.info(f"Connected stream info: {inlet}.")
    return inlet


class Stream:
    """Wrapper to the muselsl.Stream class that enables stream termination."""

    def __init__(self, muse_address):
        """Initialize stream."""
        self.muse_address = muse_address
        self._reset()

    def start(self):
        """Start stream."""
        if self.is_running():
            logger.warning("Stream process is already running.")
        else:
            self._start_stream_process()
            self._connect()
        return self.is_running()

    def stop(self):
        """Stop stream."""
        if not self.is_running():
            logger.warning("Stream process was not running.")
        else:
            logger.info("Terminating LSL stream...")
            self.process.terminate()
            self.process.join()

            if not self.process.is_alive():
                logger.info("LSL streaming process was terminated.")
                self._reset()
            else:
                logger.error("LSL streaming process is still alive.")

        return self.is_running()

    def is_running(self):
        """Check if stream is running."""
        if None in (self.process, self.inlet):
            return False
        return self.process.is_alive()

    def pull_chunk(self, timeout=0.1):
        """Pull data chunk from the stream."""
        return self.inlet.pull_chunk(timeout=timeout)

    def get_channels_count(self):
        """Return number of channels in the connected stream."""
        if self.inlet is not None:
            return self.inlet.get_channels_count()

    def get_sampling_rate(self):
        """Return sampling rate for connected stream."""
        if self.inlet is not None:
            return self.inlet.get_sampling_rate()

    def get_channels(self):
        """Return channels info for connected stream."""
        if self.inlet is not None:
            return self.inlet.get_channels()

    def _start_stream_process(self):
        """Start new LSL stream process."""
        logger.info("Starting stream for Muse @ {muse_address}.")
        self.process = multiprocessing.Process(
            target=Stream_stream_process, args=(self.muse_address,)
        )
        self.process.start()

    def _connect(self):
        """Connect inlet to the stream if running."""
        self.inlet = find_lsl_stream()
        if self.inlet is None:
            logger.warning("Failed to find a connector.")

    def _reset(self):
        """Reset stream properties."""
        self.process = None
        self.inlet = None


class DataCollector(utils.StoppableThread):
    """Stream data processor, executes main processing loop and collects data."""

    def __init__(self, stream, buffer_size=None, *args, **kwargs):
        """Initialize data collector."""
        super().__init__(*args, **kwargs)
        self.stream = stream
        self.buffer_size = buffer_size
        self.lock = threading.Lock()
        self.running = False
        self.data = None
        self.timestamps = None
        self.clear()

    def clear(self):
        """Clear collected data."""
        self.data = [tuple([0] * self.stream.get_channels_count())]
        self.timestamps = []

    def get_data_size(self):
        """Returns the size of the data in buffer in number of samples."""
        return (
            len(self.data)
            * self.stream.get_channels_count()
            * self.stream.get_sampling_rate()
        )

    def get_data(self):
        """Returns a copy of collected data."""
        return self.data.copy()

    def get_timestamps(self):
        """Returns a copy of collected timestamps."""
        return self.timestamps.copy()

    def is_running(self):
        """Check if collector is running."""
        return self.running and not self.stopped()

    def run(self):
        """Collect data in a loop until collector is stopped."""
        self.running = True
        while not self.stopped():
            chunk, timestamps = self.stream.pull_chunk()
            with self.lock:
                self.data.extend(chunk)
                self.timestamps.extend(timestamps)
                if self.buffer_size is not None:
                    self.data = self.data[-self.buffer_size :]
                    self.timestamps = self.timestamps[-self.buffer_size :]
        self.running = False


from scipy import signal
import matplotlib.pyplot as plt
from server.plotter import SignalPlotter
import numpy as np


def compute_spectrum(X, fs, cutoff=np.inf):
    """Compute normalized frequency spectrum."""
    fft = np.abs(np.fft.fft(X)) / len(X)
    fft = fft[range(int(len(X) / 2))]

    freq = np.fft.fftfreq(len(X), 1.0 / fs)
    freq = freq[range(int(len(X) / 2))]

    index = np.where(freq < cutoff)[0][-1]
    freq = freq[:index]
    fft = fft[:index]

    return freq[1:], fft[1:]


class BandPassFilter:
    """Butterworth band pass filter.

    TODO: Do timestamps require any correction after applying filter?
    """

    def __init__(self, band, sampling, order=10):
        """Initialize butterworth bandpass filter."""
        self.band = band
        self.sampling = sampling
        self.order = order
        self.sos = signal.butter(
            N=self.order, Wn=self.band, btype="bandpass", output="sos", fs=self.sampling
        )
        self.z = np.zeros((self.sos.shape[0], 2))

    def apply(self, X):
        """Returns filtered signal."""
        Y, self.z = signal.sosfilt(self.sos, X, zi=self.z)
        return Y

    def compute_frequency_response(self, max_freq=64):
        """Plot frequency response using matplotlib."""
        w, h = signal.sosfreqz(self.sos, worN=max_freq)
        db = 20 * np.log10(np.maximum(np.abs(h), 1e-5))
        return w / np.pi, db


def generate_complex_signal(freqs, amps, duration, fs):
    """Generate complex signal that is a sum of sine waves with
    given set of frequencies and amplitudes.
    """
    ts = np.linspace(0.0, duration, int(fs * duration))
    data = sum(A * np.sin(2 * np.pi * f * ts) for A, f in zip(amps, freqs))
    return data, ts


def plot(data, title):
    "Plot data with a given title." ""
    plt.title(title)
    plt.plot(*data)
    plt.show()


import math


class RunningStats:
    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return math.sqrt(self.variance())


def neurofeedback():
    """Implement simple neurofeedback pipeline."""
    from server import configuration

    class DummyStream:
        def stop(self):
            pass

        def get_sampling_rate(self):
            return 32

        def get_channels_count(self):
            return 5

        def pull_chunk(self):
            return (np.random.randint(0, 200, (256, 4)), np.linspace(0, 10, 10))

    # stream = DummyStream()
    stream = Stream(configuration.muse.get_address())
    stream.start()
    input("press enter when stream starts...")

    filters = [
        BandPassFilter((8, 13), stream.get_sampling_rate())
        for _ in range(stream.get_channels_count())
    ]
    # plot(filters[0].compute_frequency_response(), "filter response")

    data = []

    window = stream.get_sampling_rate() * 5
    stats = RunningStats()
    prev_alpha = None

    def data_source():
        nonlocal data
        nonlocal window
        nonlocal stream
        nonlocal filters
        nonlocal stats
        nonlocal prev_alpha

        eeg, ts = stream.pull_chunk()
        eeg = np.transpose(eeg)

        data.extend(
            np.transpose(
                [bandpass.apply(channel) for channel, bandpass in zip(eeg, filters)]
            )
        )

        if len(data) > window:
            data = data[-window:]

        try:
            for x in eeg[0]:
                stats.push(x)
            alpha = np.log10(stats.variance())

            if prev_alpha is not None:
                direction = "0"
                if alpha > prev_alpha:
                    direction = "UP"
                if alpha < prev_alpha:
                    direction = "DOWN"

                print(f"{direction} {alpha}")
            prev_alpha = alpha

        except Exception as e:
            print(e)

        return data

    plotter = SignalPlotter(["A", "B", "C", "D"], data_source)
    plotter.show()

    stream.stop()


if __name__ == "__main__":
    neurofeedback()
