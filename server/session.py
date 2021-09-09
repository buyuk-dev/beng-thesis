import os
from datetime import datetime

from logger import logger

import monitor
import exporter


def add_to_playlist(item, label):
    pass


class Session:

    def __init__(self, collector):
        self.monitor = monitor.PlaybackMonitor(lambda old, new, ts: self.on_playback_change(old, new, ts))
        self.collector = collector

        self.init_new_item()
        self.userid = 0
        self.session_data_dir = "data"

    def init_new_item(self):
        self.collector.clear()

        self.markers = {
            "start": None,
            "end": None,
            "labeling": None
        }
        self.set_label(None)

    def on_playback_change(self, old, new, timestamp):
        """ TODO: Move logic detecting type of change inside the monitor,
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
        self.init_new_item()
        self.markers["start"] = timestamp

    def on_playback_stopped(self, playback_info, timestamp):
        logger.info("Playback stopped.")
        self.markers["end"] = timestamp

    def on_playback_next(self, old, new, timestamp):
        logger.info("New playback item.")
        self.markers["end"] = timestamp
        df = self._build_data_frame(old)
        path = os.path.join(self.session_data_dir, f"{timestamp}.json")
        df.save(path)
        self.init_new_item()

    def set_label(self, label):
        self.label = label
        self.markers["labeling"] = datetime.now()

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
            self.userid
        )

