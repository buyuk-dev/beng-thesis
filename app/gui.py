""" The svhitties phone in the world is a miracle.
    It's your life that sucks, around the phone.
"""

import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")

import threading
import webbrowser

from logger import logger
import configuration
import widgets
import spotify.api
import spotify.callbacks
import spotify.filters

import client

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


def spotify_connector_thread():
    """ Spotify connector process.
    """
    callback_url = configuration.SPOTIFY_CALLBACK_URL
    logger.info(f"Spotify connector at {callback_url}.")

    def on_auth_callback(code):
        logger.info("Spotify connection authorized.")

        code, resp = spotify.api.request_token(code, callback_url)
        vif (code != 200):
            logger.error(f"Spotify token request failed with HTTP {code}.")
            return

        logger.info("Spotify OAuth token received.")
        configuration.TOKEN = resp["access_token"]

        code, resp = spotify.api.get_user_profile(configuration.TOKEN)
        if code != 200:
            logger.error(f"Error getting user id: HTTP {code}.")
            return

        configuration.USER_ID = resp["id"]
        logger.info(f"Current Spotify user is {configuration.USER_ID}")

        code, resp = spotify.api.get_user_playlists(configuration.TOKEN, configuration.USER_ID)
        configuration.PLAYLISTS = spotify.filters.playlists(resp)

    httpServer = spotify.callbacks.SocketListener(on_auth_callback, callback_url)
    url = spotify.api.authorize_user(callback_url)

    httpServer.start()
    webbrowser.open(url)


class GuiApp(tk.Tk):
    """
    """

    PERIODIC_UPDATE_INTERVAL = 1000
    GRAPH_ANIMATION_INTERVAL = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def on_connect_to_spotify():
            logger.info("Connecting to spotify.")
            connector = threading.Thread(target=spotify_connector_thread)
            self.connect_to_spotify.configure(state='disabled')
            connector.start()

        def on_start_recording():
            self.start_recording.configure(state='disabled')
            self.stop_recording.configure(state='normal')

        def on_stop_recording():
            self.stop_recording.configure(state='disabled')
            self.start_recording.configure(state='normal')

        def on_app_close():
            self.destroy()

        def on_like():
            logger.info("User likes current song.")
            code, resp = spotify.api.add_item_to_playlist(
                configuration.TOKEN,
                configuration.PLAYLISTS["EEG-Liked"]["id"],
                self.playback_info["uri"]
            )

        def on_dislike(): 
            logger.info("User dislikes current song.")
            code, resp = spotify.api.add_item_to_playlist(
                configuration.TOKEN,
                configuration.PLAYLISTS["EEG-Disliked"]["id"],
                self.playback_info["uri"]
            )

        def on_meh():
            logger.info("User has no opinion about current song.")
            code, resp = spotify.api.add_item_to_playlist(
                configuration.TOKEN,
                configuration.PLAYLISTS["EEG-Meh"]["id"],
                self.playback_info["uri"]
            )

        self.protocol("WM_DELETE_WINDOW", on_app_close)
        self.title("Spotify EEG Data Collection")

        # App Frame
        self.app_frame = tk.Frame(self)
        self.app_frame.pack()

        self.start_recording = tk.Button(self.app_frame, text="Record", command=on_start_recording)
        self.start_recording.pack(side=tk.LEFT)

        self.stop_recording = tk.Button(self.app_frame, text="Stop recording", command=on_stop_recording, state='disabled')
        self.stop_recording.pack(side=tk.LEFT)

        self.connect_to_spotify = tk.Button(self.app_frame, text="Connect Spotify", command=on_connect_to_spotify)
        self.connect_to_spotify.pack(side=tk.LEFT)

        # Control Frame
        self.control_frame = tk.Frame(self)
        self.control_frame.pack()

        self.like = tk.Button(self.control_frame, text="Like", command=on_like)
        self.like.pack(side=tk.LEFT)

        self.meh = tk.Button(self.control_frame, text="Meh", command=on_meh)
        self.meh.pack(side=tk.LEFT)

        self.dislike = tk.Button(self.control_frame, text="Dislike", command=on_dislike)
        self.dislike.pack(side=tk.LEFT)

        # Song Info Box
        self.song_info = widgets.SongInfo(self, 8)
        self.song_info.pack()

        # Connection Status Box
        self.status_frame = tk.Frame(self)
        self.status_frame.pack()
        self.spotify_connection_state = tk.Label(self.status_frame, text="Disconnected")
        self.spotify_connection_state.pack()

        # Processing setup
        self.after(self.PERIODIC_UPDATE_INTERVAL, self.periodic_update)

    def periodic_update(self):
        if hasattr(configuration, "TOKEN"):
            self.spotify_connection_state.configure(text=f"Connected: {configuration.TOKEN[:10]}...")
            self.song_info.update(get_playback_info(configuration.TOKEN))
        else:
            self.connect_to_spotify.configure(state='normal')

        self.after(self.PERIODIC_UPDATE_INTERVAL, self.periodic_update)


if __name__ == '__main__':
    app = GuiApp()
    app.mainloop()

