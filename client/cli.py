""" 2021 Created by michal@buyuk-dev.com
"""

from pprint import pprint
from typing import Optional, Callable

import client
from command_parser import CommandParser
from logger import logger


class ConfigCommandParser(CommandParser):
    def __init__(self, parent):
        super().__init__("config", parent)
        self.show_command = CommandParser("show", self, self.on_show)
        self.update_command = CommandParser("update", self, self.on_update)

    @staticmethod
    def on_show():
        pprint(client.get_config(0))

    @staticmethod
    def on_update():
        raise NotImplementedError()


class SpotifyCommandParser(CommandParser):
    def __init__(self, parent):
        super().__init__("spotify", parent)
        self.connect_command = CommandParser("connect", self, self.on_connect)
        self.playback_command = CommandParser("playback", self, self.on_playback)
        self.status_command = CommandParser("status", self, self.on_status)

    @staticmethod
    def on_connect():
        pprint(client.connect_spotify())

    @staticmethod
    def on_playback():
        pprint(client.get_current_playback())

    @staticmethod
    def on_status():
        pprint(client.spotify_status())


class MuseCommandParser(CommandParser):
    def __init__(self, parent):
        super().__init__("muse", parent)
        self.connect_command = CommandParser("connect", self, self.on_connect)
        self.disconnect_command = CommandParser("disconnect", self, self.on_disconnect)
        self.start_command = CommandParser("start", self, self.on_start)
        self.stop_command = CommandParser("stop", self, self.on_stop)

    @staticmethod
    def on_connect():
        print(client.connect_muse())

    @staticmethod
    def on_disconnect():
        print(client.disconnect_muse())

    @staticmethod
    def on_start():
        print(client.start_muse_data_collection())

    @staticmethod
    def on_stop():
        print(client.stop_muse_data_collection())


class SessionCommandParser(CommandParser):
    def __init__(self, parent, config):
        super().__init__("session", parent)
        self.start_command = CommandParser("start", self, self.on_start)
        self.stop_command = CommandParser("stop", self, self.on_stop)
        self.label_command = CommandParser("label", self, self.on_label)
        self.label_command.add_argument("label", choices=config["labels"])

    @staticmethod
    def on_start():
        print(client.session_start())

    @staticmethod
    def on_stop():
        print(client.session_stop())

    @staticmethod
    def on_label(label):
        print(client.session_label(label))


if __name__ == "__main__":

    status, config = client.get_config(0)
    if "labels" not in config:
        logger.error("Config returned by the server doesn't contain required entry.")

    parser = CommandParser()
    config_cmd_parser = ConfigCommandParser(parser)
    spotify_cmd_parser = SpotifyCommandParser(parser)
    muse_cmd_parser = MuseCommandParser(parser)
    session_cmd_parser = SessionCommandParser(parser, config)
    parser.run()
