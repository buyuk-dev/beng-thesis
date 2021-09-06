import argparse

from logger import logger
import client
import pprint

class ConfigCommand:

    @staticmethod
    def on_config_request(args):
        userid = 0
        status, config = client.get_config(userid)
        pprint.pprint(config)

    @staticmethod
    def on_config_update(args):
        raise NotImplementedError()


class SpotifyCommand:

    @staticmethod
    def on_connect(args):
        client.connect_spotify()

    @staticmethod
    def on_playback_request(args):
        print(client.get_current_playback())

    @staticmethod
    def on_status_request(args):
        print(client.spotify_status())

    @staticmethod
    def on_mark_current_song(args):
        client.mark_current_song(args.label)


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
        raise NotImplementedError()


class SessionCommand:

    @staticmethod
    def on_start(args):
        client.start_session()

    @staticmethod
    def on_stop(args):
        client.stop_session()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="bci")
    subparsers = parser.add_subparsers()

    userid = 0
    status, config = client.get_config(userid)
    if "labels" not in config:
        logger.error("Config returned by the server doesn't contain required entry.")

    # Config Commands Parser
    config_parser = subparsers.add_parser("config")
    config_subparsers = config_parser.add_subparsers()

    config_show_parser = config_subparsers.add_parser("show")
    config_show_parser.set_defaults(command=ConfigCommand.on_config_request)

    config_update_parser = config_subparsers.add_parser("update")
    config_update_parser.set_defaults(command=ConfigCommand.on_config_update)

    # Spotify Commands Parser
    spotify_parser = subparsers.add_parser("spotify")
    spotify_subparsers = spotify_parser.add_subparsers()

    spotify_connect_parser = spotify_subparsers.add_parser("connect")
    spotify_connect_parser.set_defaults(command=SpotifyCommand.on_connect)

    spotify_playback_parser = spotify_subparsers.add_parser("playback")
    spotify_playback_parser.set_defaults(command=SpotifyCommand.on_playback_request)

    spotify_mark_parser = spotify_subparsers.add_parser("mark")
    spotify_mark_parser.set_defaults(command=SpotifyCommand.on_mark_current_song)
    spotify_mark_parser.add_argument("label", choices=config["labels"])

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

    # Session Commands Parser
    session_parser = subparsers.add_parser("session")
    session_subparsers = session_parser.add_subparsers()

    session_start_parser = session_subparsers.add_parser("start")
    session_start_parser.set_defaults(command=SessionCommand.on_start)

    session_stop_parser = session_subparsers.add_parser("stop")
    session_stop_parser.set_defaults(command=SessionCommand.on_stop)

    args = parser.parse_args()
    args.command(args)

    # Parse Commands
    args = parser.parse_args()
    args.command(args)
