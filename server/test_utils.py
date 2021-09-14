""" 2021 Created by michal@buyuk-dev.com

    Unit tests for utils.py module.
"""

import unittest
import time

from utils import StoppableThread


class TestStoppableThread(unittest.TestCase):
    """Unit test for StoppableThread class."""

    def test_stoppable_thread(self):
        class TestThread(StoppableThread):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.counter = 0

            def run(self, *args, **kwargs):
                while not self.stopped(*args, **kwargs):
                    self.counter += 1
                    time.sleep(1)

        thread = TestThread()
        thread.start()
        time.sleep(2)
        self.assertEqual(thread.counter, 2)
        self.assertFalse(thread.stopped())
        thread.stop()
        self.assertTrue(thread.stopped())
        time.sleep(2)
        self.assertEqual(thread.counter, 2)


if __name__ == "__main__":
    unittest.main()
