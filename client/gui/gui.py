""" The svhitties phone in the world is a miracle.
    It's your life that sucks, around the phone.
"""

import tkinter as tk

import configuration
import widgets
import client

from logger import logger


class GuiApp(tk.Tk):
    """ """

    PERIODIC_UPDATE_INTERVAL = 1000
    GRAPH_ANIMATION_INTERVAL = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def on_connect_to_spotify():
            client.connect_spotify()

        def on_connect_muse():
            client.connect_muse("address")

        def on_start_recording():
            self.start_recording.configure(state="disabled")
            self.stop_recording.configure(state="normal")
            client.start_muse_data_collection()

        def on_stop_recording():
            self.stop_recording.configure(state="disabled")
            self.start_recording.configure(state="normal")
            client.stop_muse_data_collection()

        def on_app_close():
            self.destroy()

        def on_like():
            logger.info("User likes current song.")
            client.mark_current_song("like")

        def on_dislike():
            logger.info("User dislikes current song.")
            client.mark_current_song("dislike")

        def on_meh():
            logger.info("User has no opinion about current song.")
            client.mark_current_song("meh")

        self.protocol("WM_DELETE_WINDOW", on_app_close)
        self.title("Spotify EEG Data Collection")

        # App Frame
        self.app_frame = tk.Frame(self)
        self.app_frame.pack()

        self.start_recording = tk.Button(
            self.app_frame, text="Record", command=on_start_recording
        )
        self.start_recording.pack(side=tk.LEFT)

        self.stop_recording = tk.Button(
            self.app_frame,
            text="Stop recording",
            command=on_stop_recording,
            state="disabled",
        )
        self.stop_recording.pack(side=tk.LEFT)

        self.connect_to_spotify = tk.Button(
            self.app_frame, text="Connect Spotify", command=on_connect_to_spotify
        )
        self.connect_to_spotify.pack(side=tk.LEFT)

        self.connect_muse = tk.Button(
            self.app_frame, text="Connect Muse", command=on_connect_muse
        )
        self.connect_muse.pack(side=tk.LEFT)

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
        code, playback = client.get_current_playback()
        if code == 200:
            self.song_info.update(playback)
        else:
            logger.error(f"get_current_playback() -> {code}, {playback}")
        self.after(self.PERIODIC_UPDATE_INTERVAL, self.periodic_update)


if __name__ == "__main__":
    app = GuiApp()
    app.mainloop()
