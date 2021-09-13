import unittest
from unittest.mock import Mock


from command_parser import CommandParser


class TestCommandParser(unittest.TestCase):
    """Unit tests for CommandParser."""

    def test_root_parser(self):
        """Test creating root parser."""
        parser = CommandParser()
        self.assertIsNotNone(parser.parser)

    def test_child_parser_no_command(self):
        """Test creating child parser without command raises error."""
        parent = CommandParser()
        with self.assertRaises(TypeError):
            CommandParser(parent=parent)

    def test_child_parser(self):
        """Test creating child parser. Should succeed."""
        parent = CommandParser()
        CommandParser(command="test", parent=parent)

    def test_child_parser_callback(self):
        """Test creating child parser with a callback."""
        callback = Mock()
        parent = CommandParser()
        parser = CommandParser(command="test", parent=parent, callback=callback)
        self.assertEqual(parser.callback, callback)

    def test_child_parser_callback_called_once(self):
        """Test using mock callback is triggered exactly once for a given command."""
        mock = Mock()
        parent = CommandParser()
        parser = CommandParser(command="test", parent=parent, callback=mock)
        parent.run(args=["test"])
        mock.assert_called_once()

    def test_child_parser_callback_arg(self):
        """Test using mock callback is triggered exactly once for a given command."""
        mock = Mock()
        parent = CommandParser()
        parser = CommandParser(command="test", parent=parent, callback=mock)
        parser.add_argument("arg0", help="Argument 0")
        parent.run(args=["test", "test"])
        mock.assert_called_once_with(arg0="test")


if __name__ == "__main__":
    unittest.main()
