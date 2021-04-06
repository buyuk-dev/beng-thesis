from muselsl import stream, list_muses
from pylsl import StreamInlet, resolve_byprop
import threading
import pprint
import time

import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation

from logger import logger
import configuration


class MuseEegStream:

    def __init__(self, muse_address=configuration.MAC_ADDRESS):
        self.muse_address = muse_address
        self.data_lock = threading.Lock()

    def _parse_channel_names(self):
        ch = self.inlet.info().desc().child("channels").child("channel")
        self.channel_names = []
         
        for k in range(self.nchannels):
            self.channel_names.append(ch.child_value("label"))
            ch = ch.next_sibling()

    def connect(self):
        """ Setup Muse LSL connection.
        """
        def stream_thread():
            stream(self.muse_address, ppg_enabled=True, acc_enabled=True, gyro_enabled=True)

        self.stream_thread = threading.Thread(target=stream_thread)
        self.stream_thread.start()
        time.sleep(5.0)
        print("LSL stream started.")

        self.streams = resolve_byprop('type', 'EEG', timeout=2)
        if len(self.streams) == 0:
            raise RuntimeError('Failed to start EEG stream.')

        print("Streams resolved.")

        self.inlet = StreamInlet(self.streams[0], max_chunklen=30)

        print("Inlet created.")

        self.sampling = int(self.inlet.info().nominal_srate())
        self.nchannels = self.inlet.info().channel_count()

        self._parse_channel_names()
        print(self.channel_names)

        print(f"Stream sampling rate {self.sampling},") 
        print(f"Stream number of channels {self.nchannels}.")

        self.window_size = self.sampling * 3
        self.data = [tuple([0] * self.nchannels)] * self.window_size

    def start(self):
        """ Start reading samples.
        """
        def collect_data():
            while True:
                new_data, timestamps = self.inlet.pull_chunk(timeout=0.1)
                print(new_data[0])
                with self.data_lock:
                    self.data.extend(new_data)
                    self.data = self.data[-self.window_size:]
       
        self.collect_thread = threading.Thread(target=collect_data)
        self.collect_thread.start()


class SignalPlotter:

    def __init__(self, channels, data_source):
        self.channel_names = channels
        self.nchannels = len(channels)
        self.data_source = data_source

        self.fig = pyplot.figure()
        self.axs = []

        for i in range(self.nchannels):
            title = self.channel_names[i]
            print(f"Adding subplot for {title}")
            ax = self.fig.add_subplot(self.nchannels, 1, i + 1)
            ax.set_title(title)
            self.axs.append(ax)

    def clear(self):
        for ax in self.axs:
            ax.clear()

    def set_ylim(self, ymin, ymax):
        [ax.set_ylim([ymin, ymax]) for ax in self.axs]

    def draw(self, event):
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
        ani = FuncAnimation(self.fig, self.draw, interval=100)
        pyplot.show() 


if __name__ == '__main__':

    muse_stream = MuseEegStream()
    muse_stream.connect()
    muse_stream.start()

    def data_source():
        with muse_stream.data_lock:
            return muse_stream.data.copy()

    plotter = SignalPlotter(muse_stream.channel_names, data_source)
    plotter.show()    
