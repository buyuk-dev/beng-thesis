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


def get_playback_info(token):
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
    return flask.make_response("OK", 200)


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
    logger.info(f"Marking song as {value}.")
    if value not in configuration.MARK_TO_PLAYLIST_NAME:
        logger.error(f"Invalid mark value: {value}.")
        return flask.make_response(f"Invalid mark: {value}.", 400)

    current_playback_info = get_playback_info(configuration.TOKEN)
    if current_playback_info is None:
        return flask.make_response(f"Failed to get current playback from Spotify.", 400)

    playlist_name = configuration.MARK_TO_PLAYLIST_NAME[value]
    playlist = configuration.PLAYLISTS[playlist_name]

    logger.debug(f"Adding current track {current_playback_info['song']} to {playlist_name}.")
    code, resp = spotify.api.add_item_to_playlist(
        configuration.TOKEN,
        playlist["id"],
        current_playback_info["uri"]
    )

    if code != 200:
        return flask.make_response(resp, code)

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


