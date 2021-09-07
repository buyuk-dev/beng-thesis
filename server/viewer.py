import os
import sys
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np

import exporter


def plot_data(df):
    """ df:
            timestamps: dictionary with 3 datetime objects under 'start', 'end', and 'labeling' keys.
            eeg_data: 2d array of eeg signal.
            playback_info: dictionary storing info about the spotify playback for which the signal was recorded.
            userid: subject's user id.
    """

    data = np.array(df.eeg_data)
    print(data.shape)

    # Swap data columns with rows.
    data = data.swapaxes(0, 1)
    print(data.shape)

    start = df.timestamps['start']
    end = df.timestamps['end']
    labeling = df.timestamps['labeling']

    print('timestamps')
    print(f'start: {start} -> {start.timestamp()}')
    print(f'labeling: {labeling} -> {labeling.timestamp()}')
    print(f'end: {end} -> {end.timestamp()}')

    plt.xlabel('Time (s)')
    plt.ylabel('EEG Signal')
    plt.title(f'EEG Signal for {df.userid}')

    # Compute timestamps for each sample based on <start; end> range using linear interpolation.
    start_timestamp = start.timestamp()
    end_timestamp = end.timestamp()
    labeling_timestamp = labeling.timestamp()
    timestamps = np.linspace(start_timestamp, end_timestamp, data.shape[1])

    # Plot each channel of a signal on separate subplot, using timestamps for x axis.
    for i in range(data.shape[0]):
        plt.subplot(data.shape[0], 1, i + 1)
        plt.plot(timestamps - start_timestamp, data[i])

        # Mark labeling timestamp using a vertical, red line.
        plt.axvline(x=labeling_timestamp - start_timestamp, color='red')

        # Add labels.
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (mA)')

    plt.show()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("path")

    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"File {path} not found.")

    df = exporter.DataFrame.load(args.path)
    plot_data(df)

