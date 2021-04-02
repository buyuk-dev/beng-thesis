from muselsl import stream, list_muses
from pylsl import StreamInlet, resolve_byprop

MAC_ADDRESS = "00:55:DA:B5:7E:45"

## This is synchronous command.
## How to make it run asynchronously until stop signal?
# stream(MAC_ADDRESS)

streams = resolve_byprop('type', 'EEG', timeout=2)
if len(streams) == 0:
    raise RuntimeError('Failed to start EEG stream.')

inlet = StreamInlet(streams[0], max_chunklen=12)
eeg_time_correction = inlet.time_correction()

info = inlet.info()
description = info.desc()

sampling = int(info.nominal_srate())
print(info.as_xml())


