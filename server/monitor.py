import time
from datetime import datetime

from logger import logger

import spotify.api
import spotify.filters

from utils import StoppableThread
import configuration


def get_current_playback_info(token):
    """Request current playback from Spotify API."""
    if token is None:
        logger.error("Spotify API access token unavailable.")
        return

    code, playback_info = spotify.api.get_current_playback_info(token)

    if code == 204:
        logger.warning("Looks like nothing is playing at the moment.")
        return

    if code != 200:
        logger.error(f"Error getting current playback: HTTP {code}.")
        return

    return spotify.filters.playback_info(playback_info)


class PlaybackMonitor(StoppableThread):
    def __init__(self, playback_change_callback, *args, **kwargs):
        """playback_change_callback:
        Function that will be called when playback change is detected.
        It will receive the following arguments:
            old_info: playback info before the change
            new_info: playback info after the change
            timestamp: change detection timestamp
        """
        super().__init__(*args, **kwargs)
        self.playback_info = None
        self.playback_change_callback = playback_change_callback

    def _has_playback_changed(self, old, new):
        """Determine if both playback_info objects represent the same playback item."""
        if old is None and new is None:
            return False
        if old is None or new is None:
            return True
        return old["uri"] != new["uri"]

    def run(self, poll_interval=1):
        """Keeps polling playback info from Spotify to determine if it has changed."""
        while not self.stopped():
            token = configuration.spotify.get_token()
            new_playback_info = get_current_playback_info(token)
            if self._has_playback_changed(self.playback_info, new_playback_info):
                self.on_playback_change(new_playback_info)
            self.playback_info = new_playback_info
            time.sleep(poll_interval)

    def on_playback_change(self, playback_info):
        """Callback for when playback changes."""
        timestamp = datetime.now()
        self.playback_change_callback(self.playback_info, playback_info, timestamp)


if __name__ == "__main__":

    # The expected outcome of this test is that the callback is called twice.
    import unittest.mock

    def playback_change_callback(old, new, timestamp):
        print(f"Playback changed at {timestamp}")

    # Mock access token for Spotify API
    configuration.spotify.get_token = lambda: "MOCK_TOKEN"

    with unittest.mock.patch(
        "spotify.api.get_current_playback_info"
    ) as mock_get_current_playback_info:
        mock_get_current_playback_info.side_effect = [
            (
                200,
                {
                    "is_playing": True,
                    "item": {
                        "uri": "spotify:track:123",
                        "name": "Test track",
                        "album": {"name": "test", "release_date": "2021-03-04"},
                        "artists": [{"name": "test"}],
                        "duration_ms": 123,
                        "popularity": 10,
                    },
                    "progress_ms": 0,
                },
            ),
            (
                200,
                {
                    "is_playing": True,
                    "item": {
                        "uri": "spotify:track:456",
                        "name": "Another test track",
                        "album": {"name": "test", "release_date": "2021-03-04"},
                        "artists": [{"name": "test2"}],
                        "popularity": 10,
                        "duration_ms": 123,
                    },
                    "progress_ms": 0,
                },
            ),
            (204, None),
        ]

        playback_monitor = PlaybackMonitor(playback_change_callback)
        playback_monitor.start()

        time.sleep(3)
        playback_monitor.stop()
