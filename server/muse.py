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
        data, ts = self.inlet.pull_chunk(timeout=timeout)
        return data, [t + self.inlet.time_correction() for t in ts]

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
