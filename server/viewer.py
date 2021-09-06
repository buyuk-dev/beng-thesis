import os
import sys
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np

import exporter



def plot_data(df):
    data = np.array(df.eeg_data)
    print(data.shape)

    # Swap data columns with rows.
    data = data.swapaxes(0, 1)
    print(data.shape)

    # Plot each data channel on a separate subplots arranged one under the other.
    for i in range(data.shape[0]):
        plt.subplot(data.shape[0], 1, i+1)
        plt.plot(data[i])

    plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("path")

    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"File {path} not found.")

    df = exporter.DataFrame.load(args.path)
    plot_data(df)

