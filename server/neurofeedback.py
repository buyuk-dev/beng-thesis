""" 2021 Created by michal@buyuk-dev.com
"""

import numpy as numpy

from server import configuration
from server.muse import Stream
from server.plotter import SignalPlotter
from server.filter import BandPassFilter
from server import utils
from utils import generate_complex_signal, plot, compute_spectrum


def neurofeedback():
    """Implement simple neurofeedback pipeline."""

    stream = Stream(configuration.muse.get_address())
    stream.start()
    input("press enter when stream starts...")

    filters = [
        BandPassFilter((12, 32), stream.get_sampling_rate())
        for _ in range(stream.get_channels_count())
    ]

    data = []

    window = stream.get_sampling_rate() * 10
    stats = utils.RunningStats()
    prev_alpha = None

    # Ignore first batch as its likely empty
    stream.pull_chunk()

    def data_source():
        nonlocal data
        nonlocal window
        nonlocal stream
        nonlocal filters
        nonlocal stats
        nonlocal prev_alpha

        var_channel = 1

        eeg, ts = stream.pull_chunk()
        eeg = numpy.transpose(eeg)

        data.extend(
            numpy.transpose(
                [bandpass.apply(channel) for channel, bandpass in zip(eeg, filters)]
            )
        )

        if len(data) > window:
            data = data[-window:]

        try:
            print("computing spectrum...")
            return compute_spectrum(
                numpy.transpose(data)[var_channel], stream.get_sampling_rate(), 35
            )
        except Exception as e:
            print(e)
            return None

        try:
            for x in eeg[var_channel]:
                stats.push(x)
            alpha = numpy.log10(stats.variance())

            if prev_alpha is not None:
                direction = "0"
                if alpha > prev_alpha:
                    direction = "UP"
                if alpha < prev_alpha:
                    direction = "DOWN"

                print(f"{direction} {alpha}")
            prev_alpha = alpha

        except Exception as e:
            print(e)

        return numpy.transpose(data)

    plotter = SignalPlotter(["TP9 spectrum"], data_source)
    # plotter = SignalPlotter(["TP9", "AF7", "AF8", "TP10", "AUX"], data_source)
    plotter.show()

    stream.stop()


if __name__ == "__main__":
    neurofeedback()
