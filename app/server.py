import flask
import threading
import time
import webbrowser

from logger import logger
import configuration
import spotify.api
import spotify.filters


server = flask.Flask("EegDataCollectionServer")
server.debug = False


@server.route("/callback")
def spotify_auth_callback():
    logger.info("Spotify auth callback has been triggered.")
    auth_code = flask.request.args.get("code", None)
    if auth_code == None:
        logger.error(f"Spotify auth callback triggered with no auth code.")
        return flask.make_response("Error: Auth code is None.", 401)

    logger.debug(f"Auth code is {auth_code}")
    code, resp = spotify.api.request_token(auth_code, configuration.SPOTIFY_CALLBACK_URL)
    if code != 200:
        logger.error(f"Failed to retrieve access token: HTTP {code}.")
        return flask.make_response(resp, code)
    token = resp["access_token"]

    code, resp = spotify.api.get_user_profile(token)
    if code != 200:
        logger.error(f"Failed to retireve user profile info: HTTP {code}.")
        return flask.make_response(resp, code)
    user_id = resp["id"]

    code, resp = spotify.api.get_user_playlists(token, user_id)
    if code != 200:
        logger.error(f"Failed to retrieve user's playlists: HTTP {code}.")
        return flask.make_response(resp, code)

    configuration.PLAYLISTS = spotify.filters.playlists(resp)
    configuration.USER_ID = user_id
    configuration.TOKEN = token

    logger.debug(f"token = {configuration.TOKEN}")
    logger.debug(f"user_id = {configuration.USER_ID}")
    logger.debug(f"playlists = {configuration.PLAYLISTS}")

    return flask.make_response("OK", 200)


@server.route("/mark/<value>")
def on_mark_song_command(value):
    logger.info(f"Marking song as {value},")
    return flask.make_response("OK", 200)


@server.route("/spotify/connect")
def on_spotify_connect():
    logger.info("Connecting to Spotify...")
    auth_url = spotify.api.authorize_user(configuration.SPOTIFY_CALLBACK_URL)
    webbrowser.open(auth_url)
    return flask.make_response("OK", 200)


@server.route("/muse/connect/<address>")
def on_muse_connect(address):
    logger.info(f"Attempting connection to Muse 2 device at {address}...")
    return flask.make_response("OK", 200)


class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class ServerThread(StoppableThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stopped():
            logger.info("ServerThread main loop is running...")
            time.sleep(1)


if __name__ == "__main__":
    server_thread = ServerThread()
    server_thread.start()
    server.run()


