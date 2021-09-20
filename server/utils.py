""" 2021 Created by michal@buyuk-dev.com
"""

import threading
import math

import numpy
from matplotlib import pyplot


def compute_spectrum(X, fs, cutoff=numpy.inf):
    """Compute normalized frequency spectrum."""
    fft = numpy.abs(numpy.fft.fft(X)) / len(X)
    fft = fft[range(int(len(X) / 2))]

    freq = numpy.fft.fftfreq(len(X), 1.0 / fs)
    freq = freq[range(int(len(X) / 2))]

    index = numpy.where(freq < cutoff)[0][-1]
    freq = freq[:index]
    fft = fft[:index]

    return freq[1:], fft[1:]


def generate_complex_signal(freqs, amps, duration, fs):
    """Generate complex signal that is a sum of sine waves with
    given set of frequencies and amplitudes.
    """
    ts = numpy.linspace(0.0, duration, int(fs * duration))
    data = sum(A * numpy.sin(2 * numpy.pi * f * ts) for A, f in zip(amps, freqs))
    return data, ts


def plot(data, title):
    "Plot data with a given title." ""
    pyplot.title(title)
    pyplot.plot(*data)
    pyplot.show()


class RunningStats:
    """Imprementation found on StackOverflow and copied from:
    https://github.com/liyanage/python-modules/blob/master/running_stats.py
    """

    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return math.sqrt(self.variance())


class StoppableThread(threading.Thread):
    """Thread wrapper that adds stop() function."""

    def __init__(self, *args, **kwargs):
        """Initialize thread."""
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        """Stop running thread."""
        self._stop_event.set()

    def stopped(self):
        """Check if thread is stopped."""
        return self._stop_event.is_set()
