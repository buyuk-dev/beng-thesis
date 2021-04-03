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


data = []


fig = pyplot.figure()
ax = fig.add_subplot(111)


def draw(event):
    global data
    global ax
    ax.clear()
    ax.plot(data[-200:])
    data = data[-400:]


ani = FuncAnimation(fig, draw, interval=100)

print("shwoing plot")
#pyplot.show()

chunk, timestamps = inlet.pull_chunk(timeout=1.0)
data = list(chunk)

while True:
    new_data, timestamps = inlet.pull_chunk()
    data.extend(new_data)




sampling = int(info.nominal_srate())
print(info.as_xml())


