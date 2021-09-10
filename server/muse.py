""" 2021 Created by michal@buyuk-dev.com
"""

import threading
import multiprocessing

from matplotlib import pyplot
from matplotlib.animation import FuncAnimation

import muselsl
import pylsl

import configuration
from logger import logger
import utils


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


class SignalPlotter:
    """Plot signal in real time using matplotlib."""

    def __init__(self, channels, data_source):
        """Initialize plotter."""
        self.channel_names = channels
        self.nchannels = len(channels)
        self.data_source = data_source

        self.fig = pyplot.figure()
        self.axs = []

        for i in range(self.nchannels):
            title = self.channel_names[i]
            ax = self.fig.add_subplot(self.nchannels, 1, i + 1)
            ax.set_title(title)
            self.axs.append(ax)

    def clear(self):
        """Clear all subplots."""
        for ax in self.axs:
            ax.clear()

    def set_ylim(self, ymin, ymax):
        """Set y axis range."""
        for ax in self.axs:
            ax.set_ylim([ymin, ymax])

    def draw(self, *_args):
        """Plot data."""
        self.clear()
        self.set_ylim(-200, 200)

        data = self.data_source()

        data_channels = [[d[i] for d in data] for i in range(self.nchannels)]

        for n, ax in enumerate(self.axs):
            ax.set_title(self.channel_names[n])

        for ax, channel in zip(self.axs, data_channels):
            ax.plot(channel)

    def show(self):
        """Show matplotlib window."""
        _ = FuncAnimation(self.fig, self.draw, interval=100)
        pyplot.show()


def main_plot():
    """Function that connects to a muse device and displays live data graph."""
    stream = Stream(configuration.muse.get_address())
    stream.start()

    collector = DataCollector(stream, 3)
    collector.start()

    def data_source():
        """ """
        with collector.lock:
            return collector.data.copy()

    plotter = SignalPlotter(stream.channels, data_source)
    plotter.show()

    collector.stop()
    stream.stop()


if __name__ == "__main__":
    main_plot()
