""" 2021 Created by michal@buyuk-dev.com
"""

import numpy
import time
from pylsl import StreamInfo, StreamOutlet, local_clock


class MockEegStream:

    CHANNEL_NAMES = ['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX']
    SAMPLING_RATE = 256
    SAMPLE_TYPE = 'float32'
    UNIQUE_ID = "MockMuse"
    MANUFACTURER = "Muse"
    SAMPLE_UNIT = "microvolts"
    STREAM_TYPE = "EEG"
    EEG_CHUNK = 12

    def __init__(self):
        self.eeg_info = StreamInfo(
            self.MANUFACTURER,
            self.STREAM_TYPE,
            len(self.CHANNEL_NAMES),
            self.SAMPLING_RATE,
            self.SAMPLE_TYPE,
            self.UNIQUE_ID
        )

        self.eeg_info.desc().append_child_value(
            "manufacturer",
            self.MANUFACTURER
        )

        eeg_channels = self.eeg_info.desc().append_child("channels")

        for channel_name in self.CHANNEL_NAMES:
            eeg_channels.append_child("channel") \
                .append_child_value("label", channel_name) \
                .append_child_value("unit", self.SAMPLE_UNIT) \
                .append_child_value("type", self.STREAM_TYPE)

        # chunk_size can be overriden by StreamInlet.
        # optional arg: max_buffered speicies max amount of data to buffer.
        #               by default it is set to 6 minutes of data.
        # TODO: Can max_buffered buffer size be related to the stream breaking off?

        self.eeg_outlet = StreamOutlet(self.eeg_info, self.EEG_CHUNK)
        self.ts = local_clock()

        self.timer_start = self.ts
        self.timer_sample_count = 0

    def push_samples(self):
        now = local_clock() # returns current timestamp in seconds.
        dt = now - self.ts
        sample_count = int(dt * self.SAMPLING_RATE)

        if now - self.timer_start > 1.0:
            print(f"within last second {self.timer_sample_count} samples were pushed.")
            self.timer_sample_count = 0
            self.timer_start = now

        self.timer_sample_count += sample_count

        timestamps = numpy.linspace(self.ts, now, sample_count)
        data = [
            numpy.sin(2.0 * numpy.pi * freq * timestamps)
            for freq in [5.0, 10.0, 15.0, 20.0, 60.0]
        ]

        self.ts = now
        for sample, timestamp in zip(numpy.transpose(data), timestamps):
            self.eeg_outlet.push_sample(sample, timestamp)


def main():
    stream = MockEegStream()
    while True:
        stream.push_samples()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
