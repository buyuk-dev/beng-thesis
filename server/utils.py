""" 2021 Created by michal@buyuk-dev.com
"""

import threading


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
