""" @author:  Michal Michalski ( michal@buyuk-dev.com )
    @summary: Data collection app configuration management
"""
import json
import os
import sys

import secret


CONFIGURATION_DIR = "configs"


def _determine_platform():
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "linux":
        return "linux"
    else:
        return None


def _get_config_path(filename, check_if_exists=True):
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
        """ Load Spotify config from JSON file """
        with open(filename) as f:
            data = json.load(f)
            spotify = cls()
            spotify.set_client_id(data['client_id'])
            spotify.set_client_secret(data['client_secret'])
            spotify.set_callback_url(data['callback_url'])
            spotify.set_playlists(data['playlists'])
            spotify.set_user_id(data['user_id'])
            return spotify

    def save(self, filename):
        """ Save Spotify config to JSON file """
        with open(filename, 'w') as f:
            data = {
                'client_id': self.get_client_id(),
                'client_secret': self.get_client_secret(),
                'callback_url': self.get_callback_url(),
                'playlists': self.get_playlists(),
                'user_id': self.get_user_id()
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
        """ Load Muse config from JSON file """
        with open(filename) as f:
            data = json.load(f)
            muse = cls()
            muse.set_name(data['name'])
            muse.set_address(data['address'])
            return muse

    def save(self, filename):
        """ Save Muse config to JSON file """
        with open(filename, 'w') as f:
            data = {
                'name': self.get_name(),
                'address': self.get_address(),
            }
            json.dump(data, f)


class App:

    def __init__(self):
        self.set_labels_to_playlists_map(None)

    def get_labels_to_playlists_map(self):
        return self.labels_to_playlists_map

    def set_labels_to_playlists_map(self, new_map):
        self.labels_to_playlists_map = new_map

    @classmethod
    def load(cls, filename):
        """ Load App config from JSON file """
        with open(filename) as f:
            data = json.load(f)
            app = cls()
            app.set_labels_to_playlists_map(data['labels_to_playlists_map'])
            return app

    def save(self, filename):
        """ Save App config to JSON file """
        with open(filename, 'w') as f:
            data = {
                'labels_to_playlists_map': self.get_labels_to_playlists_map(),
            }
            json.dump(data, f)


spotify = None
muse = None
app = None


def reset_configuration():
    global spotify
    global muse
    global app

    spotify = Spotify()
    spotify.set_client_id(secret.SPOTIFY_CLIENT_ID)
    spotify.set_client_secret(secret.SPOTIFY_CLIENT_SECRET)
    spotify.set_callback_url("http://localhost:5000/callback")
    spotify.save(_get_config_path("spotify.json", False))

    muse = Muse()
    muse.set_name("Muse-7E45")
    if _determine_platform() == "macos":
        muse.set_address(secret.MUSE_UUID_ADDRESS)
    else:
        muse.set_address(secret.MUSE_MAC_ADDRESS)
    muse.save(_get_config_path("muse.json", False))

    app = App()
    app.set_labels_to_playlists_map({
        "like": "EEG-Liked",
        "dislike": "EEG-Disliked",
        "meh": "EEG-Meh"
    })
    app.save(_get_config_path("app.json", False))


def load_configuration():
    global spotify
    global muse
    global app

    spotify = Spotify.load(_get_config_path("spotify.json"))
    muse = Muse.load(_get_config_path("muse.json"))
    app = App.load(_get_config_path("app.json"))


def get_config_view(userid):
    global spotify
    global muse
    global app

    config_view = {
        "labels": list(app.get_labels_to_playlists_map().keys())
    }
    return config_view


def update_config(userid, partial_config_json):
    global spotify
    global muse
    global app
    logger.warning("Config update requested, but currently user isn't allowed to change any settings.")


if __name__ == '__main__':
    reset_configuration()
else:
    load_configuration()
