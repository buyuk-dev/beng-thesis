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
        self.playback_info = playback_info
        self.eeg_data = eeg_data
        self.timestamps = timestamps
        self.label = label
        self.userid = userid
        self._encoding = "utf-8"

    def serialize_eeg(self):
        eeg = pickle.dumps(self.eeg_data)
        eeg = base64.b64encode(eeg)
        return eeg.decode(self._encoding)

    def save(self, filename, format="json"):
        directory = os.path.dirname(filename)
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
            else:
                raise TypeError(f"{type(obj)} is not JSON serializable.")

        with open(filename, "w") as output_file:
            json.dump(data, output_file, default=datetime_jsonify)

    def __str__(self):
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
    def load(cls, filename, format="json"):
        with open(filename, "r") as input_file:
            data = json.load(input_file)

        eeg = data["eeg"]
        eeg = base64.b64decode(eeg)
        eeg = pickle.loads(eeg)

        timestamps = data["timestamps"]
        for key in timestamps:
            timestamps[key] = datetime.fromisoformat(timestamps[key])

        return cls(
            data["playback"], eeg, data["timestamps"], data["label"], data["userid"]
        )


if __name__ == "__main__":

    # Create an example of DataFrame object
    eeg_data = np.random.rand(100, 10)
    playback_info = {
        "playback_id": "12345",
        "playback_start": "2020-01-01 12:00:00",
        "playback_end": "2020-01-01 12:00:10",
    }
    timestamps = {
        "labeling_start": "2020-01-01 12:00:05",
        "labeling_end": "2020-01-01 12:00:10",
    }
    label = "happy"
    userid = "12345"

    df = DataFrame(playback_info, eeg_data, timestamps, label, userid)

    # Export data to a test file. The file will be in json format
    df.save("test.json")

    # Import data from the test file into new DataFrame object. The file must be in json format
    df2 = DataFrame.load("test.json")
    print(df2)
