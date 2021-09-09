import time
import threading
import multiprocessing

import flask
import webbrowser

from logger import logger

import configuration

import spotify.api
import spotify.filters

import muse
import session

import utils


g_server = flask.Flask("EegDataCollectionServer")
g_server.debug = True


g_stream = None
g_collector = None
g_session = None


@g_server.route("/user/<userid>/config")
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


@g_server.route("/spotify/connect")
def on_spotify_connect():
    logger.info("Connecting to Spotify...")
    auth_url = spotify.api.authorize_user(configuration.spotify.get_callback_url())
    webbrowser.open(auth_url)
    return {}, 200


@g_server.route("/spotify/status")
def on_spotify_status():
    logger.info("Requesting spotify connection status...")
    response = {
        "status": configuration.spotify.get_token() is not None
    }
    return response, 200


@g_server.route("/spotify/playback")
def on_spotify_playback():
    logger.info("Requesting current spotify playback info...")
    if configuration.spotify.get_token() is None:
        logger.error(f"Spotify unauthorized.")
        return {"error": f"Spotify not authorized."}, 401

    current_playback_info = session.monitor.get_current_playback_info(configuration.spotify.get_token())
    if current_playback_info is None:
        return {"error": "Failed to get current playback info from Spotify."}, 400

    return current_playback_info, 200


@g_server.route("/callback")
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


@g_server.route("/muse/connect/<address>")
def on_muse_connect(address):
    global g_stream
    global g_collector

    logger.info(f"Attempting connection to Muse 2 device at {address}.")

    if g_stream is None:
        g_stream = muse.Stream(configuration.muse.get_address())

    g_stream.start()

    if g_collector is None:
        g_collector = muse.DataCollector(g_stream)

    return {}, 200


@g_server.route("/muse/start")
def on_muse_start_stream():
    global g_collector

    if g_collector is None:
        logger.error("There is no active LSL stream.")
        return {"error": "Muse needs to be connected before streaming is possible."}, 400

    logger.info(f"Starting data stream.")
    g_collector.start()

    return {}, 200


@g_server.route("/muse/stop")
def on_muse_stop_stream():
    global g_collector

    if g_collector is None:
        logger.error("There is no active LSL stream.")
        return {"error": "Muse is not connected."}, 400

    logger.info("Stopping data collection.")
    g_collector.stop()

    return {}, 200


@g_server.route("/muse/disconnect")
def on_muse_disconnect():
    global g_stream

    if g_stream is None:
        logger.error("There is no active LSL stream.")
        return {"error": "Muse is not connected."}, 400

    logger.info(f"Disconnecting muse device.")
    g_stream.stop()

    return {}, 200


@g_server.route("/muse/status")
def on_muse_status():
    global g_stream
    global g_collector

    logger.info(f"Requesting muse device status.")
    response = {
        "stream": g_stream is not None and g_stream.is_running(),
        "collector": g_collector is not None and g_collector.is_running()
    }

    return response, 200


@g_server.route("/session/start")
def on_session_start():
    global g_session
    global connector

    logger.info("Starting session.")
    if configuration.spotify.get_token() is None:
        return {"error": "Spotify access token unavailable. Connect to Spotify."}, 400

    if g_stream is None or not g_stream.is_running():
        return {"error": "Muse is not connected. Connect to Muse."}, 400

    if g_collector is None:
        return {"error": "Data collection needs to be started first."}, 400

    g_session = session.Session(g_collector)
    g_session.start()

    return {}, 200


@g_server.route("/session/stop")
def on_session_stop():
    logger.info("Stopping session.")

    global g_session
    if g_session is None:
        return {"error": "No active session exists."}, 400

    g_session.stop()
    return {}, 200


@g_server.route("/session/label/<label>")
def on_session_label(label):
    """ This function does the same thing as on_mark() endpoint, but using a different url.
        Additionally, if there is an active session it sets label for that session.
    """
    logger.info(f"Labeling current song in a session as {label}.")

    global g_session
    if g_session is None:
        return {"error": "No active session exists."}, 400

    g_session.set_label(label)
    return {}, 200


if __name__ == "__main__":
    g_server.run()

