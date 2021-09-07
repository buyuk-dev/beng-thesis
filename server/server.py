""" Usage:
    0. GET /system/config/<userid> --> get app settings
    1. POST /system/config/<userid> --> update app settings
    2. GET /spotify/connect --> spotify callback at /callback
    3. GET /mark/<MARK_TO_PLAYLIST_NAME> --> label current playback
    4. GET /muse/connect/<address> --> connect muse device and start LSL stream
    5. GET /muse/start --> start collecting Muse data
    6. GET /muse/stop --> stop collecting Muse data
    7. GET /muse/disconnect --> disconnect Muse device
    8. GET /muse/plot --> display real-time plot of muse data
    9. GET /spotify/status --> get spotify connection status
    10. GET /spotify/playback --> get current playback info
    11. GET /muse/status --> get muse stream and data collection status
"""

import os
import sys
import flask
import threading
import multiprocessing
import time
from datetime import datetime
import webbrowser

from logger import logger

import configuration
import spotify.api
import spotify.filters
import muse
import utils
import monitor
import exporter

server = flask.Flask("EegDataCollectionServer")
server.debug = True


# TODO: Remove global state.
stream = None
collector = None
session = None


class Session:

    def __init__(self):
        self.monitor = monitor.PlaybackMonitor(lambda old, new, ts: self.on_playback_change(old, new, ts))
        self.init_new_item()
        self.userid = 0 # Currently userid is not used for anything.
        self.session_data_dir = "data"

    def init_new_item(self):
        global collector
        collector.clear()

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
        global collector
        return exporter.DataFrame(
            playback_info,
            collector.get_data(),
            self.markers,
            self.label,
            self.userid
        )


@server.route("/user/<userid>/config")
def on_system_config(userid):
    if flask.request.method == 'GET':
        logger.info("User requests configuration.");
        return configuration.get_config_view(userid), 200
    elif flask.request.method == 'POST':
        logger.info("User wants to update configuration.");
        status = configuration.update_config(userid, flask.request.json)
        return configuration.get_config_view(userid), 200
    else:
        logger.error("Unsupported request method.");
        return {"error": "Invalid request method, must be GET or POST."}, code


@server.route("/spotify/connect")
def on_spotify_connect():
    logger.info("Connecting to Spotify...")
    auth_url = spotify.api.authorize_user(configuration.spotify.get_callback_url())
    webbrowser.open(auth_url)
    return {}, 200


@server.route("/spotify/status")
def on_spotify_status():
    logger.info("Requesting spotify connection status...")
    response = {
        "status": configuration.spotify.get_token() is not None
    }
    return response, 200


@server.route("/spotify/playback")
def on_spotify_playback():
    logger.info("Requesting current spotify playback info...")
    if configuration.spotify.get_token() is None:
        logger.error(f"Spotify unauthorized.")
        return {"error": f"Spotify not authorized."}, 401

    current_playback_info = monitor.get_current_playback_info(configuration.spotify.get_token())
    if current_playback_info is None:
        return {"error": "Failed to get current playback from Spotify."}, 400

    return current_playback_info, 200


@server.route("/callback")
def spotify_auth_callback():
    logger.info("Spotify auth callback has been triggered.")
    auth_code = flask.request.args.get("code", None)
    if auth_code == None:
        logger.error(f"Spotify auth callback triggered with no auth code.")
        return {"error": "Auth code is None."}, 401

    logger.debug(f"Auth code is {auth_code}")
    code, resp = spotify.api.request_token(auth_code, configuration.spotify.get_callback_url())
    if code != 200:
        logger.error(f"Failed to retrieve access token: HTTP {code}.")
        return {"error": resp}, code
    token = resp["access_token"]

    code, resp = spotify.api.get_user_profile(token)
    if code != 200:
        logger.error(f"Failed to retireve user profile info: HTTP {code}.")
        return {"error": resp}, code
    user_id = resp["id"]

    code, resp = spotify.api.get_user_playlists(token, user_id)
    if code != 200:
        logger.error(f"Failed to retrieve user's playlists: HTTP {code}.")
        return {"error": resp}, code

    configuration.spotify.set_playlists(spotify.filters.playlists(resp))
    configuration.spotify.set_user_id(user_id)
    configuration.spotify.set_token(token)

    logger.debug(f"token = {configuration.spotify.get_token()}")
    logger.debug(f"user_id = {configuration.spotify.get_user_id()}")
    logger.debug(f"playlists = {configuration.spotify.get_playlists()}")

    return {}, 200


@server.route("/mark/<value>")
def on_mark_song_command(value):
    logger.info(f"Marking song as {value}.")
    if value not in configuration.app.get_labels_to_playlists_map():
        logger.error(f"Invalid mark value: {value}.")
        return {"error": f"Invalid mark: {value}."}, 400

    current_playback_info = get_current_playback_info(configuration.spotify.get_token())
    if current_playback_info is None:
        return {"error": f"Failed to get current playback from Spotify."}, 400

    playlist_name = configuration.app.get_labels_to_playlists_map()[value]
    playlist = configuration.spotify.get_playlists()[playlist_name]

    logger.debug(f"Adding current track {current_playback_info['song']} to {playlist_name}.")
    code, resp = spotify.api.add_item_to_playlist(
        configuration.get_token(),
        playlist["id"],
        current_playback_info["uri"]
    )

    if code != 200:
        return {"error": resp}, code

    return {}, 200


@server.route("/muse/connect/<address>")
def on_muse_connect(address):
    global stream
    global collector

    logger.info(f"Attempting connection to Muse 2 device at {address}.")

    if stream is None:
        stream = muse.Stream(configuration.muse.get_address())

    stream.start()

    if collector is None:
        collector = muse.DataCollector(stream)

    return {}, 200


@server.route("/muse/start")
def on_muse_start_stream():
    global collector
    logger.info(f"Starting data stream.")
    collector.start()
    return {}, 200


@server.route("/muse/stop")
def on_muse_stop_stream():
    global collector
    logger.info("Stopping data collection.")
    collector.stop()
    return {}, 200


@server.route("/muse/disconnect")
def on_muse_disconnect():
    global stream
    logger.info(f"Disconnecting muse device.")
    stream.stop()
    return {}, 200


@server.route("/muse/status")
def on_muse_status():
    logger.info(f"Requesting muse device status.")
    global stream
    response = {
        "stream": stream is not None and stream.is_running(),
        "collector": collector is not None and collector.is_running()
    }
    return response, 200


@server.route("/muse/plot")
def on_muse_plot():
    """ This probably doesnt make much sense... """
    global stream
    global collector
    logger.info(f"Plotting muse data.")

    if collector is None:
        return {"error": "Data collector is not set."}, 400

    def data_source():
        global collector
        with collector.lock:
            return collector.data.copy()

    plotter = muse.SignalPlotter(stream.channels, data_source)
    plotter.show()

    return {}, 200


@server.route("/session/start")
def on_session_start():
    logger.info("Starting session.")
    if configuration.spotify.get_token() is None:
        return {"error": "Spotify access token unavailable. Connect to Spotify."}, 400

    if stream is None or not stream.is_running():
        return {"error": "Muse is not connected. Connect to Muse."}, 400

    if collector is None:
        return {"error": "Data collection needs to be started first."}, 400

    global session
    session = Session()
    session.start()
    return {}, 200


@server.route("/session/stop")
def on_session_stop():
    logger.info("Stopping session.")

    global session
    if session is None:
        return {"error": "No active session exists."}, 400

    session.stop()
    return {}, 200


@server.route("/session/label/<label>")
def on_session_label(label):
    """ This function does the same thing as on_mark() endpoint, but using a different url.
        Additionally, if there is an active session it sets label for that session.
    """
    logger.info(f"Labeling current song in a session as {label}.")

    global session
    if session is None:
        return {"error": "No active session exists."}, 400

    session.set_label(label)
    return {}, 200



if __name__ == "__main__":
    server.run()

