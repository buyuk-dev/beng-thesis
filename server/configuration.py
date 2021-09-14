""" @author:  Michal Michalski ( michal@buyuk-dev.com )
    @summary: Data collection app configuration management
"""
import json
import os
import sys

from server.logger import logger
import server.secret


CONFIGURATION_DIR = "configs"

spotify = None
muse = None
app = None


def _determine_platform():
    """ Determine operating system the app is running on. """
    if sys.platform == "darwin":
        return "macos"

    if sys.platform in ["win32", "cygwin"]:
        return "windows"

    if sys.platform == "linux":
        return "linux"

    return None


def _get_config_path(filename, check_if_exists=True):
    """ Get config file path. """
    if not os.path.exists(CONFIGURATION_DIR):
        os.makedirs(CONFIGURATION_DIR)

    path = os.path.join(CONFIGURATION_DIR, filename)
    if not os.path.isfile(path) and check_if_exists:
        raise FileNotFoundError(path)

    return path


class Spotify:

    def __init__(self):
        self.set_client_id(None)
        self.set_client_secret(None)
        self.set_callback_url(None)
        self.set_token(None)
        self.set_playlists(None)
        self.set_user_id(None)

    def get_client_id(self):
        return self.client_id

    def set_client_id(self, new_id):
        self.client_id = new_id

    def get_client_secret(self):
        return self.client_secret

    def set_client_secret(self, new_secret):
        self.client_secret = new_secret

    def get_callback_url(self):
        return self.callback_url

    def set_callback_url(self, new_url):
        self.callback_url = new_url

    def get_token(self):
        return self.token

    def set_token(self, new_token):
        self.token = new_token

    def get_playlists(self):
        return self.playlists

    def set_playlists(self, new_playlists):
        self.playlists = new_playlists

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, new_id):
        self.user_id = new_id

    @classmethod
    def load(cls, filename):
        """Load Spotify config from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            config = cls()
            config.set_client_id(data["client_id"])
            config.set_client_secret(data["client_secret"])
            config.set_callback_url(data["callback_url"])
            config.set_playlists(data["playlists"])
            config.set_user_id(data["user_id"])
            return config

    def save(self, filename):
        """Save Spotify config to JSON file"""
        with open(filename, "w", encoding='utf-8') as f:
            data = {
                "client_id": self.get_client_id(),
                "client_secret": self.get_client_secret(),
                "callback_url": self.get_callback_url(),
                "playlists": self.get_playlists(),
                "user_id": self.get_user_id(),
            }
            json.dump(data, f, indent=4)


class Muse:

    def __init__(self):
        self.set_name(None)
        self.set_address(None)

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_address(self):
        return self.address

    def set_address(self, new_address):
        self.address = new_address

    @classmethod
    def load(cls, filename):
        """Load Muse config from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            config = cls()
            config.set_name(data["name"])
            config.set_address(data["address"])
            return config

    def save(self, filename):
        """Save Muse config to JSON file"""
        with open(filename, "w", encoding='utf-8') as f:
            data = {
                "name": self.get_name(),
                "address": self.get_address(),
            }
            json.dump(data, f)


class App:

    def __init__(self):
        self.set_labels_to_playlists_map(None)
        self.set_session_data_dir(None)

    def get_labels_to_playlists_map(self):
        return self.labels_to_playlists_map

    def set_labels_to_playlists_map(self, new_map):
        self.labels_to_playlists_map = new_map

    def get_session_data_dir(self):
        return self.session_data_dir

    def set_session_data_dir(self, new_dir):
        self.session_data_dir = new_dir

    @classmethod
    def load(cls, filename):
        """Load App config from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            config = cls()
            config.set_labels_to_playlists_map(data["labels_to_playlists_map"])
            config.set_session_data_dir(data["session_data_dir"])
            return config

    def save(self, filename):
        """Save App config to JSON file"""
        with open(filename, "w", encoding='utf-8') as f:
            data = {
                "labels_to_playlists_map": self.get_labels_to_playlists_map(),
                "session_data_dir": self.get_session_data_dir(),
            }
            json.dump(data, f)


def reset_configuration():
    global spotify
    global muse
    global app

    spotify = Spotify()
    spotify.set_client_id(secret.SPOTIFY_CLIENT_ID)
    spotify.set_client_secret(secret.SPOTIFY_CLIENT_SECRET)
    #spotify.set_callback_url("http://localhost:5000/callback")
    spotify.set_callback_url("http://0.0.0.0:8000/callback")
    spotify.save(_get_config_path("spotify.json", False))

    muse = Muse()
    muse.set_name("Muse-7E45")
    if _determine_platform() == "macos":
        muse.set_address(secret.MUSE_UUID_ADDRESS)
    else:
        muse.set_address(secret.MUSE_MAC_ADDRESS)
    muse.save(_get_config_path("muse.json", False))

    app = App()
    app.set_labels_to_playlists_map(
        {"like": "EEG-Liked", "dislike": "EEG-Disliked", "meh": "EEG-Meh"}
    )
    app.set_session_data_dir("data")
    app.save(_get_config_path("app.json", False))


def load_configuration():
    global spotify
    global muse
    global app

    spotify = Spotify.load(_get_config_path("spotify.json"))
    muse = Muse.load(_get_config_path("muse.json"))
    app = App.load(_get_config_path("app.json"))


def get_config_view(_userid):
    global spotify
    global muse
    global app

    config_view = {"labels": list(app.get_labels_to_playlists_map().keys())}
    return config_view


def update_config(_userid, partial_config_json):
    global spotify
    global muse
    global app
    logger.warning(
        "Config update requested, but currently user isn't allowed to change any settings."
    )


if __name__ == "__main__":
    reset_configuration()
else:
    load_configuration()
