""" 2021 Created by michal@buyuk-dev.com
"""

import os
import argparse

from matplotlib import pyplot
import numpy as np

import exporter


def plot_data(data_frame):
    """data_frame:
    timestamps: dictionary with 3 datetime objects under 'start', 'end', and 'labeling' keys.
    eeg_data: 2d array of eeg signal.
    playback_info: dictionary storing info about the spotify playback for which the signal was recorded.
    userid: subject's user id.
    """

    data = np.array(data_frame.eeg_data)
    print(data.shape)

    # Swap data columns with rows.
    data = data.swapaxes(0, 1)
    print(data.shape)

    start = data_frame.timestamps["start"]
    end = data_frame.timestamps["end"]
    labeling = data_frame.timestamps["labeling"]

    print("timestamps")
    print(f"start: {start} -> {start.timestamp()}")
    print(f"labeling: {labeling} -> {labeling.timestamp()}")
    print(f"end: {end} -> {end.timestamp()}")

    pyplot.xlabel("Time (s)")
    pyplot.ylabel("EEG Signal")
    pyplot.title(f"EEG Signal for {data_frame.userid}")

    # Compute timestamps for each sample based on <start; end> range using linear interpolation.
    start_timestamp = start.timestamp()
    end_timestamp = end.timestamp()
    labeling_timestamp = labeling.timestamp()
    timestamps = np.linspace(start_timestamp, end_timestamp, data.shape[1])

    # Plot each channel of a signal on separate subplot, using timestamps for x axis.
    for i in range(data.shape[0]):
        pyplot.subplot(data.shape[0], 1, i + 1)
        pyplot.plot(timestamps - start_timestamp, data[i])

        # Mark labeling timestamp using a vertical, red line.
        pyplot.axvline(x=labeling_timestamp - start_timestamp, color="red")

        # Add labels.
        pyplot.xlabel("Time (s)")
        pyplot.ylabel("Voltage (mA)")

    pyplot.show()


def main():
    """Run viewer."""
    parser = argparse.ArgumentParser()
    parser.add_argument("path")

    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"File {args.path} not found.")

    data_frame = exporter.DataFrame.load(args.path)
    plot_data(data_frame)


if __name__ == "__main__":
    main()
