""" Usage:

    1. GET /spotify/connect --> spotify callback at /callback
    2. GET /mark/<MARK_TO_PLAYLIST_NAME> --> label current playback
    3. GET /muse/connect/<address> --> connect muse device and start LSL stream
    4. GET /muse/start --> start collecting Muse data
    5. GET /muse/stop --> stop collecting Muse data
    6. GET /muse/disconnect --> disconnect Muse device
    7. GET /muse/plot --> display real-time plot of muse data
    8. GET /spotify/status --> get spotify connection status
    9. GET /spotify/playback --> get current playback info
    10. GET /muse/status --> get muse stream and data collection status
"""

import flask
import threading
import multiprocessing
import time
import webbrowser

from logger import logger
import configuration
import spotify.api
import spotify.filters
import muse
import utils


server = flask.Flask("EegDataCollectionServer")
server.debug = True


stream = None
collector = None


def get_current_playback_info(token):
    """ Request current playback from Spotify API.
    """
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


@server.route("/spotify/connect")
def on_spotify_connect():
    logger.info("Connecting to Spotify...")
    auth_url = spotify.api.authorize_user(configuration.SPOTIFY_CALLBACK_URL)
    webbrowser.open(auth_url)
    return {}, 200


@server.route("/spotify/status")
def on_spotify_status():
    logger.info("Requesting spotify connection status...")
    response = {
        "status": configuration.TOKEN is not None
    }
    return response, 200


@server.route("/spotify/playback")
def on_spotify_playback():
    logger.info("Requesting current spotify playback info...")
    if configuration.TOKEN is None:
        logger.error(f"Spotify unauthorized.")
        return {"error": f"Spotify not authorized."}, 401

    current_playback_info = get_current_playback_info(configuration.TOKEN)
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
    code, resp = spotify.api.request_token(auth_code, configuration.SPOTIFY_CALLBACK_URL)
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

    configuration.PLAYLISTS = spotify.filters.playlists(resp)
    configuration.USER_ID = user_id
    configuration.TOKEN = token

    logger.debug(f"token = {configuration.TOKEN}")
    logger.debug(f"user_id = {configuration.USER_ID}")
    logger.debug(f"playlists = {configuration.PLAYLISTS}")

    return {}, 200


@server.route("/mark/<value>")
def on_mark_song_command(value):
    logger.info(f"Marking song as {value}.")
    if value not in configuration.MARK_TO_PLAYLIST_NAME:
        logger.error(f"Invalid mark value: {value}.")
        return {"error": f"Invalid mark: {value}."}, 400

    current_playback_info = get_current_playback_info(configuration.TOKEN)
    if current_playback_info is None:
        return {"error": f"Failed to get current playback from Spotify."}, 400

    playlist_name = configuration.MARK_TO_PLAYLIST_NAME[value]
    playlist = configuration.PLAYLISTS[playlist_name]

    logger.debug(f"Adding current track {current_playback_info['song']} to {playlist_name}.")
    code, resp = spotify.api.add_item_to_playlist(
        configuration.TOKEN,
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
        stream = muse.Stream(configuration.MUSE_MAC_ADDRESS)

    stream.start()

    if collector is None:
        collector = muse.DataCollector(stream, 5)

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


if __name__ == "__main__":
    server.run()


