import muselsl
import pylsl
import threading
import time
import multiprocessing

import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation

from logger import logger
import configuration
import utils


class StreamConnector:

    def __init__(self, stream, max_chunklen=30):
        self.stream = stream
        self.max_chunklen = max_chunklen
        self.inlet = pylsl.StreamInlet(self.stream, max_chunklen=max_chunklen)
        self.configure()

    def configure(self):
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        self.channels_count = self.inlet.info().channel_count()
        channel_xml = self.inlet.info().desc().child("channels").child("channel")

        self.channels = []
        for k in range(self.channels_count):
            self.channels.append(channel_xml.child_value("label"))
            channel_xml = channel_xml.next_sibling()

        logger.info(f"Stream(rate: {self.sampling_rate}, channels: {self.channels}).")

    @staticmethod
    def find():
        streams = pylsl.resolve_byprop('type', 'EEG', timeout=30)
        if len(streams) == 0:
            logger.error("No active streams have been found.")
            return None

        logger.info(f"Found {len(streams)} active streams.")
        for idx, stream in enumerate(streams):
            logger.info(f"{idx}: {stream}")

        logger.info("Connecting to stream #0.")
        return StreamConnector(streams[0])


def Stream_stream_process(address):
    """ needs to be a global scope, importable object due to pickling
        done in multiprocessing.
    """
    muselsl.stream(address=address, backend="bleak")


class Stream:
    """ Wrapper to the muselsl.Stream class that enables stream termination.
    """
    def __init__(self, muse_mac_address):
        """ """
        logger.info('New stream created for {muse_mac_address}')
        self.muse_mac_address = muse_mac_address
        self.running = False
        self.process = None

    def start(self, stream_timeout=5, max_chunklen=30):
        """ """
        if self.is_running():
            logger.warning("Stream process is already running...")
            self.running = True
            return True

        self.running = False
        logger.info("Start lsl stream.")

        self.process = multiprocessing.Process(
            target=Stream_stream_process,
            args=(self.muse_mac_address,)
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
        if not self.running: return False
        elif self.process is None: return False
        return self.process.is_alive()

    def stop(self):
        """ """
        if not self.is_running():
            logger.warning("Stream process was not running already...")

        logger.info("Killing lsl stream.")
        self.process.terminate()
        self.running = self.process.is_alive()


class DataCollector(utils.StoppableThread):
    """ """
    def __init__(self, stream, buffer_size=None, *args, **kwargs):
        """ """
        super().__init__(*args, **kwargs)
        self.stream = stream
        self.buffer_size = buffer_size
        self.lock = threading.Lock()
        self.running = False
        self.clear()

    def clear(self):
        self.data = [tuple([0] * self.stream.channels_count)]

    def get_data_size(self):
        return len(self.data) * self.stream.channels_count * self.stream.sampling_rate

    def get_data(self):
        return self.data.copy()

    def is_running(self):
        return self.running and not self.stopped()

    def run(self):
        """ """
        self.running = True
        while not self.stopped():
            chunk, timestamps = self.stream.inlet.pull_chunk(timeout=0.1)
            with self.lock:
                self.data.extend(chunk)
                if self.buffer_size is not None:
                    self.data = self.data[-self.buffer_size:]
        self.running = False


class SignalPlotter:
    """ """
    def __init__(self, channels, data_source):
        """ """
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
        """ """
        for ax in self.axs:
            ax.clear()

    def set_ylim(self, ymin, ymax):
        """ """
        [ax.set_ylim([ymin, ymax]) for ax in self.axs]

    def draw(self, event):
        """ """
        self.clear()
        self.set_ylim(-200, 200)

        data = self.data_source()

        data_channels = [
            [d[i] for d in data]
            for i in range(self.nchannels)
        ]

        for n, ax in enumerate(self.axs):
            ax.set_title(self.channel_names[n])

        for ax, channel in zip(self.axs, data_channels):
            ax.plot(channel)

    def show(self):
        """ """
        ani = FuncAnimation(self.fig, self.draw, interval=100)
        pyplot.show()


if __name__ == '__main__':

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
