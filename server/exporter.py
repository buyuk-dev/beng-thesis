""" 2021 Created by michal@buyuk-dev.com
"""

import os
from datetime import datetime
import json
import base64
import pickle
import numpy as np


class DataFrame:
    """Stores single package of data.
    playback_info: dictionary with the data about playback item during which the signal was collected
    eeg_data: all eeg data collected during the session
    timestamps: relevant timestamps for: playback start and end, labeling time
    label: label that was assigned by the user during session
    userid: identification of the subject for whom the data was collected
    """

    def __init__(self, playback_info, eeg_data, timestamps, label, userid):
        """Initialize DataFrame with data."""
        self.playback_info = playback_info
        self.eeg_data = eeg_data
        self.timestamps = timestamps
        self.label = label
        self.userid = userid
        self._encoding = "utf-8"

    def serialize_eeg(self):
        """Serialize eeg data for compatibility with JSON format."""
        eeg = pickle.dumps(self.eeg_data)
        eeg = base64.b64encode(eeg)
        return eeg.decode(self._encoding)

    @staticmethod
    def deserialize_eeg(eeg):
        return pickle.loads(
            base64.b64decode(eeg)
        )

    def save(self, filename):
        """Export data frame to a json file."""
        directory = os.path.dirname(filename)
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)

        data = {
            "userid": self.userid,
            "playback": self.playback_info,
            "label": self.label,
            "timestamps": self.timestamps,
            "eeg": self.serialize_eeg(),
        }

        def datetime_jsonify(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"{type(obj)} is not JSON serializable.")

        with open(filename, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, default=datetime_jsonify)

    def __str__(self):
        """Convert DataFrame to human-readable string."""
        return (
            "DataFrame object:\n"
            "userid: {0}\n"
            "playback: {1}\n"
            "label: {2}\n"
            "timestamps: {3}\n"
            "eeg: {4}".format(
                self.userid,
                self.playback_info,
                self.label,
                self.timestamps,
                self.eeg_data,
            )
        )

    @classmethod
    def load(cls, filename):
        """Import DataFrame from json file."""
        with open(filename, "r", encoding="utf-8") as input_file:
            data = json.load(input_file)

        eeg = cls.deserialize_eeg(data["eeg"])
        timestamps = data["timestamps"]
        for key in timestamps:
            timestamps[key] = datetime.fromisoformat(timestamps[key])

        return cls(
            data["playback"], eeg, data["timestamps"], data["label"], data["userid"]
        )
