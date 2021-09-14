import unittest
import os

import numpy as np
from datetime import datetime, timedelta

from exporter import DataFrame


class TestDataFrame(unittest.TestCase):
    """Test DataFrame class."""

    eeg_data = np.random.rand(100, 10)
    playback_info = {
        "playback_id": "12345",
        "playback_start": "2021-09-14T13:42:08.962783",
        "playback_end": "2021-09-14T13:45:08.962783",
    }
    timestamps = {
        "labeling_start": datetime.now() + timedelta(minutes=2),
        "labeling_end": datetime.now() + timedelta(minutes=3),
    }
    label = "happy"
    userid = "12345"

    test_file = "test.json"


    def tearDown(self):
        if os.path.isfile(self.test_file):
            os.remove(self.test_file)

    def test_init(self):
        """Test initialization of DataFrame object."""
        data_frame = DataFrame(
            self.playback_info,
            self.eeg_data,
            self.timestamps,
            self.label,
            self.userid
        )

        self.assertEqual(data_frame.playback_info, self.playback_info)
        self.assertTrue((data_frame.eeg_data == self.eeg_data).all())
        self.assertEqual(data_frame.timestamps, self.timestamps)
        self.assertEqual(data_frame.label, self.label)
        self.assertEqual(data_frame.userid, self.userid)

    def test_serialize_eeg(self):
        """Test serialization and deserialization of eeg data."""
        data_frame = DataFrame(
            self.playback_info,
            self.eeg_data,
            self.timestamps,
            self.label,
            self.userid
        )
        eeg = data_frame.serialize_eeg()
        self.assertIs(type(eeg), str)
        eeg = DataFrame.deserialize_eeg(eeg)
        self.assertTrue((eeg == self.eeg_data).all())

    def test_save(self):
        """Test saving and loading DataFrame object to a json file."""
        data_frame = DataFrame(
            self.playback_info,
            self.eeg_data,
            self.timestamps,
            self.label,
            self.userid
        )
        data_frame.save(self.test_file)
        data_frame_2 = DataFrame.load(self.test_file)

        self.assertEqual(data_frame_2.userid, data_frame.userid)
        self.assertEqual(data_frame_2.playback_info, data_frame.playback_info)
        self.assertEqual(data_frame_2.label, data_frame.label)
        self.assertEqual(data_frame_2.timestamps, data_frame.timestamps)
        self.assertTrue((data_frame_2.eeg_data == data_frame.eeg_data).all())


if __name__ == "__main__":
    unittest.main()
