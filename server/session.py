import os
from datetime import datetime

from logger import logger

import monitor
import exporter

import spotify.api
import configuration


def _add_item_to_eeg_playlist(item, label):
    """Add playback item to the playlist corresponding to the given label."""
    playlists_map = configuration.app.get_labels_to_playlists_map()

    if label not in playlists_map:
        logger.error(f"There is no playlist for {label} label.")
        return False

    playlist_name = playlists_map[label]
    playlist = configuration.spotify.get_playlists()[playlist_name]

    logger.debug(f"Adding track {item['song']} to playlist {playlist_name}")
    code, resp = spotify.api.add_item_to_playlist(
        configuration.spotify.get_token(), playlist["id"], item["uri"]
    )

    if code not in [200, 201]:
        logger.error(f"Adding item to playlist failed with HTTP {code} error: {resp}.")
        return False

    return True


class Session:
    def __init__(self, collector):
        self.monitor = monitor.PlaybackMonitor(
            lambda old, new, ts: self.on_playback_change(old, new, ts)
        )
        self.collector = collector
        self.init_new_item()
        self.userid = 0

    def reset(self):
        self.collector.clear()
        self.markers = {"start": None, "end": None, "labeling": None}

    def on_playback_change(self, old, new, timestamp):
        """TODO: Move logic detecting type of change inside the monitor,
        and replace current callback with different ones for
        specific change types.
        """
        logger.info(f"Playback change detected at {timestamp}")
        if old is None:
            self.on_playback_started(new, timestamp)
        elif new is None:
            self.on_playback_stopped(old, timestamp)
        else:
            self.on_playback_next(old, new, timestamp)

    def on_playback_started(self, playback_info, timestamp):
        logger.info("Playback has started.")
        self.reset()
        self.markers["start"] = timestamp

    def on_playback_stopped(self, playback_info, timestamp):
        logger.info("Playback stopped.")
        self.markers["end"] = timestamp

    def on_playback_next(self, old, new, timestamp):
        logger.info("New playback item.")
        self.markers["end"] = timestamp
        df = self._build_data_frame(old)
        path = os.path.join(
            configuration.app.get_session_data_dir(), f"{timestamp}.json"
        )
        df.save(path)
        self.reset()
        self.markers["start"] = timestamp

    def set_label(self, label):
        self.label = label
        self.markers["labeling"] = datetime.now()
        _add_item_to_eeg_playlist(self.monitor.playback_info, label)

    def start(self):
        self.monitor.start()

    def stop(self):
        self.monitor.stop()

    def _build_data_frame(self, playback_info):
        return exporter.DataFrame(
            playback_info,
            self.collector.get_data(),
            self.markers,
            self.label,
            self.userid,
        )
