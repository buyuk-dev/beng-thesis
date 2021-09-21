""" 2021 Created by michal@buyuk-dev.com
"""

import time
from server import configuration
from server.muse import Stream
from server.filters import BandPassFilter
from server.markers import MarkerReader


def record():
    marker_reader = MarkerReader()
    stream = Stream(configuration.muse.get_address())
    stream.start()
    input("press enter when stream starts...")

    filters = [
        BandPassFilter((1, 40), stream.get_sampling_rate())
        for _ in range(stream.get_channels_count())
    ]

    eeg = []
    timestamps = []
    markers = []

    while stream.is_running():
        chunk, ts = stream.pull_chunk()
        eeg.extend(chunk)
        timestamps.extend(ts)

        marker, ts = marker_reader.pull_sample()
        if marker is not None and ts is not None:
            print((marker, ts))
            markers.append((marker[0], ts))

        if marker[0] == "stop":
            stream.stop()
            time.sleep(2)


if __name__ == "__main__":
    record()
