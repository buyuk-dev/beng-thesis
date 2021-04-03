from muselsl import stream, list_muses
from pylsl import StreamInlet, resolve_byprop
import threading
import pprint
import time

import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation

import configuration


class MuseEegStream:

    def __init__(self, muse_address=configuration.MAC_ADDRESS):
        self.muse_address = muse_address
        self.data_lock = threading.Lock()


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

        print(f"Stream sampling rate {self.sampling},") 
        print(f"Stream number of channels {self.nchannels}.")

        print(self.inlet.info().as_xml())

        self.window_size = self.sampling * 5
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


if __name__ == '__main__':

    muse_stream = MuseEegStream()
    muse_stream.connect()
    muse_stream.start()

    fig = pyplot.figure()
    axs = [fig.add_subplot(muse_stream.nchannels, 1, i+1) for i in range(muse_stream.nchannels)]

    def draw(event):
        for ax in axs:
            ax.clear()

        with muse_stream.data_lock:
            [ax.set_ylim([-200,200]) for ax in axs]

            data_channel = [
                [d[i] for d in muse_stream.data]
                for i in range(muse_stream.nchannels)
            ]

            for ax, channel in zip(axs, data_channel):
                ax.plot(channel)

            
    ani = FuncAnimation(fig, draw, interval=100)
    pyplot.show()

