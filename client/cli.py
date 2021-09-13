""" 2021 Created by michal@buyuk-dev.com
"""

import argparse
from pprint import pprint

from logger import logger
import client


class BaseCommandParser:

    def __init__(self, parent=None, command=None):
        """ If no parent is specified, creates highest level root parser.
            Otherwise creates a subcommand parser, for which command argument is required.
        """
        if parent is None:
            self.parser = argparse.ArgumentParser()
        else:
            if type(command) is not str:
                raise TypeError("Command argument for non-root parsers must be a string.")
            self.parser = parent.subparsers.add_parser(command)

        self.parent = parent
        self.subparsers = self.parser.add_subparsers()
        self.commands = dict()

    def define_command(self, name, callback):
        """ Defines a command recognized by the parser.
            Running parser with `<parser> command [command args]` syntax will trigger callback.
        """
        if name in self.commands:
            logger.warning(f"Overriding command parser for: {name}.")

        self.commands[name] = self.subparsers.add_parser(name)
        self.commands[name].set_defaults(command=callback)

    def add_command_argument(self, name, *args, **kwargs):
        """ Subcommands that take arguments require specification of those arguments.
        """
        self.commands[name].add_argument(*args, **kwargs)

    def run(self):
        """ Parse arguments and trigger command handler. """
        args = self.parser.parse_args()
        args.command(args)


class ConfigCommandParser(BaseCommandParser):

    def __init__(self, parent):
        super().__init__(command="config", parent=parent)
        self.define_command("show", self.on_show)
        self.define_command("update", self.on_update)

    @staticmethod
    def on_show(args):
        pprint(client.get_config(0))

    @staticmethod
    def on_update(args):
        raise NotImplementedError()


class SpotifyCommandParser(BaseCommandParser):

    def __init__(self, parent):
        super().__init__(command="spotify", parent=parent)
        self.define_command("connect", self.on_connect)
        self.define_command("playback", self.on_playback)
        self.define_command("status", self.on_status)

    @staticmethod
    def on_connect(args):
        pprint(client.connect_spotify())

    @staticmethod
    def on_playback(args):
        pprint(client.get_current_playback())

    @staticmethod
    def on_status(args):
        pprint(client.spotify_status())


class MuseCommandParser(BaseCommandParser):

    def __init__(self, parent):
        super().__init__(command="muse", parent=parent)
        self.define_command("connect", self.on_connect)
        self.define_command("disconnect", self.on_disconnect)
        self.define_command("start", self.on_start)
        self.define_command("stop", self.on_stop)

    @staticmethod
    def on_connect(args):
        print(client.connect_muse())

    @staticmethod
    def on_disconnect(args):
        print(client.disconnect_muse())

    @staticmethod
    def on_start(args):
        print(client.start_muse_data_collection())

    @staticmethod
    def on_stop(args):
        print(client.stop_muse_data_collection())


class SessionCommandParser(BaseCommandParser):

    def __init__(self, parent, config):
        super().__init__(command="session", parent=parent)
        self.define_command("start", self.on_start)
        self.define_command("stop", self.on_stop)
        self.define_command("label", self.on_label)
        self.add_command_argument("label", "label", choices=config["labels"])

    @staticmethod
    def on_start(args):
        print(client.session_start())

    @staticmethod
    def on_stop(args):
        print(client.session_stop())

    @staticmethod
    def on_label(args):
        print(client.session_label(args.label))


if __name__ == "__main__":

    status, config = client.get_config(0)
    if "labels" not in config:
        logger.error("Config returned by the server doesn't contain required entry.")

    parser = BaseCommandParser()
    config_cmd_parser = ConfigCommandParser(parser)
    spotify_cmd_parser = SpotifyCommandParser(parser)
    muse_cmd_parser = MuseCommandParser(parser)
    session_cmd_parser = SessionCommandParser(parser, config)
    parser.run()
