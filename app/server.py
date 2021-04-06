import flask
import threading
import time

from logger import logger


server = flask.Flask("EegDataCollectionServer")
server.debug = False


@server.route("/callback")
def spotify_auth_callback():
    logger.info("Spotify auth callback has been triggered.")
    code = flask.request.args.get("code", None)
    logger.info(f"Spotify authorization code: {code}")
    return flask.make_response("OK", 200)


@server.route("/mark/<value>")
def on_mark_song_command(value):
    logger.info(f"Marking song as {value},")
    return flask.make_response("OK", 200)


@server.route("/spotify/connect")
def on_spotify_connect():
    logger.info("Connecting to Spotify...")
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


