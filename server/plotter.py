""" 2021 Created by michal@buyuk-dev.com

    Custom implementation of real-time EEG viewer using matplotlib.
"""

from matplotlib import pyplot
from matplotlib.animation import FuncAnimation

# from server.muse import DataCollector, Stream


class SignalPlotter:
    """Plot signal in real time using matplotlib."""

    def __init__(self, channels, data_source):
        """Initialize plotter."""
        self.channel_names = channels
        self.nchannels = len(channels)
        self.data_source = data_source

        self.fig = pyplot.figure()
        self.axs = []

        for i in range(self.nchannels):
            title = self.channel_names[i]
            ax = self.fig.add_subplot(self.nchannels, 1, i + 1)
            ax.set_title(title)
            self.axs.append(ax)

    def clear(self):
        """Clear all subplots."""
        for ax in self.axs:
            ax.clear()

    def set_ylim(self, ymin, ymax):
        """Set y axis range."""
        for ax in self.axs:
            ax.set_ylim([ymin, ymax])

    def draw(self, *_args):
        """Plot data."""
        self.clear()

        data = self.data_source()

        # If data is a tuple its most likely a spectrum.
        if type(data) is tuple:
            self.set_ylim(0, 2)
            for n, ax in enumerate(self.axs):
                ax.set_title(self.channel_names[0])
            self.axs[0].plot(*data)
            return

        self.set_ylim(-200, 200)
        data_channels = [[d[i] for d in data] for i in range(self.nchannels)]

        for n, ax in enumerate(self.axs):
            ax.set_title(self.channel_names[n])

        for ax, channel in zip(self.axs, data):
            ax.plot(channel)


    def show(self):
        """Show matplotlib window."""
        _ = FuncAnimation(self.fig, self.draw, interval=20)
        pyplot.show()


# def main_plot():
#    """Function that connects to a muse device and displays live data graph."""
#    stream = Stream(configuration.muse.get_address())
#    stream.start()
#
#    collector = DataCollector(stream, 3)
#    collector.start()
#
#    def data_source():
#        """ """
#        with collector.lock:
#            return collector.data.copy()
#
#    plotter = SignalPlotter(stream.channels, data_source)
#    plotter.show()
#
#    collector.stop()
#    stream.stop()
#
#
# if __name__ == "__main__":
#    main_plot()
