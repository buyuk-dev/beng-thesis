from muselsl import stream, list_muses
from pylsl import StreamInlet, resolve_byprop
import threading
import pprint

import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation

MAC_ADDRESS = "00:55:DA:B5:7E:45"


def start_stream():
    """
    """
    stream(MAC_ADDRESS)


stream_thread = threading.Thread(target=start_stream)
stream_thread.start()


streams = resolve_byprop('type', 'EEG', timeout=2)
if len(streams) == 0:
    raise RuntimeError('Failed to start EEG stream.')


inlet = StreamInlet(streams[0], max_chunklen=12)
eeg_time_correction = inlet.time_correction()
info = inlet.info()
description = info.desc()


data = [(0,0,0,0)] * 1024
data_lock = threading.Lock()


def collect_data():
    global data
    chunk, timestamps = inlet.pull_chunk(timeout=0.1)
    data = list(chunk)

    while True:
        new_data, timestamps = inlet.pull_chunk(timeout=0.1)
        with data_lock:
            data.extend(new_data)


fig = pyplot.figure()
axs = [fig.add_subplot(411), fig.add_subplot(412), fig.add_subplot(413), fig.add_subplot(414)]

def draw(event):
    global data
    global axs

    for ax in axs:
        ax.clear()

    with data_lock:
        data = data[-1024:]
        data_0 = [d[0] for d in data]
        data_1 = [d[1] for d in data]
        data_2 = [d[2] for d in data]
        data_3 = [d[3] for d in data]

        [ax.set_ylim([-200,200]) for ax in axs]

        axs[0].plot(data_0)
        axs[1].plot(data_1)
        axs[2].plot(data_2)
        axs[3].plot(data_3)


collect_thread = threading.Thread(target=collect_data)
collect_thread.start()

ani = FuncAnimation(fig, draw, interval=100)
pyplot.show()


sampling = int(info.nominal_srate())
print(info.as_xml())

