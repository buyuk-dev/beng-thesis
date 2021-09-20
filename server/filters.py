""" 2021 Created by michal@buyuk-dev.com
"""
import numpy
from scipy import signal


class BandPassFilter:
    """Butterworth band pass filter.

    TODO: Do timestamps require correction after applying filter?
    """

    def __init__(self, band, sampling, order=10):
        """Initialize butterworth bandpass filter."""
        self.band = band
        self.sampling = sampling
        self.order = order
        self.sos = signal.butter(
            N=self.order, Wn=self.band, btype="bandpass", output="sos", fs=self.sampling
        )
        self.z = numpy.zeros((self.sos.shape[0], 2))

    def apply(self, X):
        """Returns filtered signal."""
        Y, self.z = signal.sosfilt(self.sos, X, zi=self.z)
        return Y

    def compute_frequency_response(self, max_freq=64):
        """Plot frequency response using matplotlib."""
        w, h = signal.sosfreqz(self.sos, worN=max_freq)
        db = 20 * numpy.log10(np.maximum(np.abs(h), 1e-5))
        return w / np.pi, db
