""" 2021 Created by michal@buyuk-dev.com
"""

import numpy as np
from matplotlib import pyplot as plt

import time
from server import configuration
from server.muse import Stream
from server.filters import BandPassFilter
from server.markers import MarkerReader


# TODO: Marker timestamps are very different than muse eeg timestamps.
#       This needs to be fixed to compute epochs.


def find_timestamp(timestamps, t):
    """Find index of the first timestamp in timestamps list greater than or eual t."""
    for idx, ts in enumerate(timestamps):
        if ts >= t:
            return idx
    return None


def record():
    marker_reader = MarkerReader()
    stream = Stream(configuration.muse.get_address())
    stream.start()
    nchannels = stream.get_channels_count()
    input("press enter when stream starts...")

    filters = [
        BandPassFilter((1, 40), stream.get_sampling_rate()) for _ in range(nchannels)
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

    # Filtering
    eeg = np.transpose(eeg)
    print(f"eeg shape: {eeg.shape}")

    print("timestamp head")
    print(timestamps[:10])

    filtered = []
    for fil, channel in zip(filters, eeg):
        filtered.append(fil.apply(channel))
    print(f"filtered shape: {len(filtered)}, {len(filtered[0])}")

    fig, axs = plt.subplots(nchannels)
    for idx, ch in enumerate(filtered):
        axs[idx].plot(ch)
    plt.show()

    # Extracting epochs grouped by events
    grouped_epochs = {}
    for marker, timestamp in markers:
        if marker in ["start", "stop"]:
            continue

        idx = find_timestamp(timestamps, timestamp)
        print(f"marker ts idx {idx}")
        if marker not in grouped_epochs:
            grouped_epochs[marker] = []
        grouped_epochs[marker].append(
            [channel[idx : idx + 256] for channel in filtered]
        )

    print("Grouped epochs:")
    for k, v in grouped_epochs.items():
        print(f"{k} : {len(v)}, {len(v[0])}")

    # Compute averages
    averages = {}
    for event, epochs in grouped_epochs.items():
        averages[event] = []
        for c in range(nchannels):
            averages[event].append(sum(e[c] for e in epochs) / len(epochs))

    print("Averages:")
    for k, v in averages.items():
        print(f"{k}: {len(v)}")

    # Plot averages
    markers = averages.keys()
    fig, axs = plt.subplots(nchannels, len(markers))
    for idx, marker in enumerate(markers):
        axs[0, idx].set_title(marker)

    for column, epoch in enumerate(averages.items()):
        marker, eeg = epoch
        for row, channel in enumerate(eeg):
            axs[row, column].plot(channel)

    plt.show()


if __name__ == "__main__":
    record()
