from muselsl import stream, list_muses
from pylsl import StreamInlet, resolve_byprop
import threading
import pprint

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

while True:

    sample, timestamp = inlet.pull_sample()
    pprint.pprint(timestamp)
    pprint.pprint(sample)





sampling = int(info.nominal_srate())
print(info.as_xml())


