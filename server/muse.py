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
import numpy as np


def compute_spectrum(X, fs, cutoff=np.inf):
    """ Compute normalized frequency spectrum.
    """
    fft = np.abs(np.fft.fft(X)) / len(X)
    fft = fft[range(int(len(X) / 2))]

    freq = np.fft.fftfreq(len(X), 1.0 / fs)
    freq = freq[range(int(len(X) / 2))]

    index = np.where(freq < cutoff)[0][-1]
    freq = freq[:index]
    fft = fft[:index]

    return freq[1:], fft[1:]


def neurofeedback():

    from server import configuration

    # Design bandpass butterworth IIR filter for <8-13>Hz band.

    fs = 256
    nyq = fs * 0.5
    low, high = 5, 40
    sos = signal.butter(
        N=10,
        Wn=(low, high),
        btype='bandpass',
        output='sos',
        fs=fs
    )

    # Generate complex signal
    freq_comp = [10, 60]
    amp_comp = [1, 0.1]
    duration = 60.0
    ts = np.linspace(.0, duration, int(fs * duration))
    data = sum(A * np.sin(2 * np.pi * f * ts) for A, f in zip(amp_comp, freq_comp))

    plt.title("generated signal")
    plt.plot(ts, data)
    plt.show()

    # Plot spectrue
    freqs, amps = compute_spectrum(data, fs)
    plt.title("signal spectrum")
    plt.plot(freqs, amps)
    plt.show()

    # Plot filter frequency responose.
    w, h = signal.sosfreqz(sos, worN=64)
    db = 20 * np.log10(np.maximum(np.abs(h), 1e-5))
    plt.title("freq response")
    plt.plot(w/np.pi, db)
    plt.show()
   
    # Filter signal
    filtered = signal.sosfilt(sos, data)
    plt.title("offline filtered")
    plt.plot(filtered)
    plt.show()

    # Plot spectrue
    freqs, amps = compute_spectrum(filtered, fs)
    plt.title("offline filtered spectrum")
    plt.plot(freqs, amps)
    plt.show()


    # Simulate real-time signal
    received = 0
    chunk_size = 10
    z = np.zeros((sos.shape[0], 2))
    filtered = []
    while received < data.shape[0]:
        received += chunk_size
        out, z = signal.sosfilt(sos, data[received - chunk_size:received], zi=z)
        filtered.extend(out)
    plt.title("real-time")
    plt.plot(filtered)
    plt.show()

    return

    # Run processing.
    stream = Stream(configuration.muse.get_address())
    stream.start()

    sampling = stream.get_sampling_rate()
    window = 10 * sampling

    collector = DataCollector(stream, window)
    collector.start()

    while True:
        data = collector.get_data()

        # Apply bandpass filter to all channels in the data:
        filtered = []
        for channel in data:
            filtered.append(
                utils.butter_bandpass_filter(
                    channel,
                    configuration.neurofeedback.get_low_cutoff(),
                    configuration.neurofeedback.get_high_cutoff(),
                    sampling,
                    order=3,
                )
            )

        
        


if __name__ == '__main__':
    neurofeedback()
