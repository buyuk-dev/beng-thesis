import argparse

from logger import logger


class CommandParser:
    def __init__(self, command=None, parent=None, callback=None):
        self.parent = parent
        self.callback = callback
        self.command = command

        self.parser = None
        self.subparsers = None

        if parent is None:
            self._init_root_parser()
        else:
            self._init_child_parser()

        self.parser.set_defaults(command=callback)

    def _init_root_parser(self):
        self.parser = argparse.ArgumentParser()

    def _init_child_parser(self):
        if type(self.command) is not str:
            raise TypeError("Command argument for non-root parsers must be a string.")

        if self.parent.subparsers is None:
            self.parent.subparsers = self.parent.parser.add_subparsers()

        self.parser = self.parent.subparsers.add_parser(self.command)

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def run(self, args=None):
        args = self.parser.parse_args(args)
        if not hasattr(args, "command"):
            self.parser.print_help()
            exit(1)

        command = args.command
        args = vars(args)
        del args["command"]
        command(**args)
