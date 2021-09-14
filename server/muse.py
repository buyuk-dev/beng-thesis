""" 2021 Created by michal@buyuk-dev.com
"""

import threading
import multiprocessing

import muselsl
import pylsl

from server import configuration
from server.logger import logger

from server import utils


class StreamConnector:
    """Find and configure LSL stream."""

    def __init__(self, stream, max_chunklen=30):
        """Initialize StreamConnector."""
        self.stream = stream
        self.max_chunklen = max_chunklen
        self.inlet = pylsl.StreamInlet(self.stream, max_chunklen=max_chunklen)
        self.configure()

    def configure(self):
        """Configure stream connector."""
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        self.channels_count = self.inlet.info().channel_count()
        channel_xml = self.inlet.info().desc().child("channels").child("channel")

        self.channels = []
        for _ in range(self.channels_count):
            self.channels.append(channel_xml.child_value("label"))
            channel_xml = channel_xml.next_sibling()

        logger.info(f"Stream(rate: {self.sampling_rate}, channels: {self.channels}).")

    @staticmethod
    def find():
        """Resolve existing LSL stream with EEG data."""
        streams = pylsl.resolve_byprop("type", "EEG", timeout=30)
        if len(streams) == 0:
            logger.error("No active streams have been found.")
            return None

        logger.info(f"Found {len(streams)} active streams.")
        for idx, stream in enumerate(streams):
            logger.info(f"{idx}: {stream}")

        logger.info("Connecting to stream #0.")
        return StreamConnector(streams[0])


# DO NOT CHANGE THIS FUNCTION, READ DOCSTRING
def Stream_stream_process(address):
    """needs to be a global scope, importable object due to pickling
    done in multiprocessing.
    """
    muselsl.stream(address=address, backend="bleak")


class Stream:
    """Wrapper to the muselsl.Stream class that enables stream termination."""

    def __init__(self, muse_mac_address):
        """Initialize stream."""
        logger.info("New stream created for {muse_mac_address}")
        self.muse_mac_address = muse_mac_address
        self.running = False
        self.process = None
        self.inlet = None
        self.sampling_rate = None
        self.channels_count = None
        self.channels = None

    def start(self):
        """Start stream."""
        if self.is_running():
            logger.warning("Stream process is already running...")
            self.running = True
            return True

        self.running = False
        logger.info("Start lsl stream.")

        self.process = multiprocessing.Process(
            target=Stream_stream_process, args=(self.muse_mac_address,)
        )
        self.process.start()

        connector = StreamConnector.find()
        if connector is None:
            logger.warning("Failed to find a connector.")
            return False

        self.inlet = connector.inlet
        self.sampling_rate = connector.sampling_rate
        self.channels_count = connector.channels_count
        self.channels = connector.channels

        self.running = True
        return True

    def is_running(self):
        """Check if stream is running."""
        if not self.running:
            return False

        if self.process is None:
            return False

        return self.process.is_alive()

    def stop(self):
        """Stop stream."""
        if not self.is_running():
            logger.warning("Stream process was not running already...")

        logger.info("Killing lsl stream.")
        self.process.terminate()
        self.running = self.process.is_alive()


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
        self.data = [tuple([0] * self.stream.channels_count)]
        self.timestamps = []

    def get_data_size(self):
        """Returns the size of the data in buffer in number of samples."""
        return len(self.data) * self.stream.channels_count * self.stream.sampling_rate

    def get_data(self):
        """Returns a copy of collected data."""
        return self.data.copy()

    def is_running(self):
        """Check if collector is running."""
        return self.running and not self.stopped()

    def run(self):
        """Collect data in a loop until collector is stopped."""
        self.running = True
        while not self.stopped():
            chunk, timestamps = self.stream.inlet.pull_chunk(timeout=0.1)
            with self.lock:
                self.data.extend(chunk)
                self.timestamps.extend(timestamps)
                if self.buffer_size is not None:
                    self.data = self.data[-self.buffer_size :]
                    self.timestamps = self.timestamps[-self.buffer_size :]
        self.running = False
