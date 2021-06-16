import argparse

from logger import logger
import configuration
import client

class SpotifyCommand:

    @staticmethod
    def on_connect(args):
        client.connect_spotify()
    

class MuseCommand:

    @staticmethod
    def on_connect(args):
        client.connect_muse("address")

    @staticmethod
    def on_disconnect(args):
        client.disconnect_muse()

    @staticmethod
    def on_start(args):
        client.start_muse_data_collection()

    @staticmethod
    def on_stop(args):
        client.stop_muse_data_collection()

    @staticmethod
    def on_plot(args):
        """ TODO: make this non-blocking by plotting client-side.
        """
        client.muse_blocking_data_plot()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="bci")
    subparsers = parser.add_subparsers()

    # Spotify Commands Parser
    spotify_parser = subparsers.add_parser("spotify")
    spotify_subparsers = spotify_parser.add_subparsers()
    spotify_connect_parser = spotify_subparsers.add_parser("connect")
    spotify_connect_parser.set_defaults(command=SpotifyCommand.on_connect)

    # Muse Commands Parser
    muse_parser = subparsers.add_parser("muse")
    muse_subparsers = muse_parser.add_subparsers()

    muse_connect_parser = muse_subparsers.add_parser("connect")
    muse_connect_parser.set_defaults(command=MuseCommand.on_connect)

    muse_connect_parser = muse_subparsers.add_parser("disconnect")
    muse_connect_parser.set_defaults(command=MuseCommand.on_disconnect)

    muse_start_parser = muse_subparsers.add_parser("start")
    muse_start_parser.set_defaults(command=MuseCommand.on_start)

    muse_stop_parser = muse_subparsers.add_parser("stop")
    muse_stop_parser.set_defaults(command=MuseCommand.on_stop)

    muse_plot_parser = muse_subparsers.add_parser("plot")
    muse_plot_parser.set_defaults(command=MuseCommand.on_plot)

    # Parse Commands
    args = parser.parse_args()
    args.command(args)

