""" The shitties phone in the world is a miracle.
    It's your life that sucks, around the phone.
"""

import tkinter as tk
import tkinter.ttk as ttk

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as pyplot
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import math
import random
from datetime import datetime

import threading
import time
import webbrowser

import configuration
import widgets
import spotify.api
import spotify.callbacks


DATA_X = [0] * 100
DATA_Y = list(range(100))


def filter_playback_info(playback_info):
    """ Extract only the required info from Spotify API response.
    """
    return {
        "artists":      playback_info["item"]["artists"][0]["name"],
        "song":         playback_info["item"]["name"],
        "popularity":   playback_info["item"]["popularity"],
        "album":        playback_info["item"]["album"]["name"],
        "released":     playback_info["item"]["album"]["release_date"],
        "duration":     playback_info["item"]["duration_ms"] // 1000,
        "progress":     playback_info["progress_ms"] // 1000
    }


def get_playback_info(token):
    """ Request current playback from Spotify API.
    """
    assert token is not None, "Access token not available."

    code, playback_info = spotify.api.get_current_playback_info(token)

    assert code == 200, f"Error getting current playback: {code}."
    assert playback_info is not None, "Looks like nothing is playing at the moment."

    return filter_playback_info(playback_info)


class ProcessorThread(threading.Thread):
    """
    """
    def __init__(self, *args, **kwargs):
        super(ProcessorThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        global DATA_X
        while not self.stopped():
            try:
                DATA_X = [random.random() for i in range(100)]
                time.sleep(0.1)

            except Exception as e:
                print(e)
                break


class GuiApp(tk.Tk):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def on_connect_to_spotify():
            callback_url = "http://localhost:5000/callback"

            def on_auth_callback(code):
                code, resp = spotify.api.request_token(code, callback_url)
                configuration.TOKEN = resp["access_token"]

            httpServer = spotify.callbacks.SocketListener(on_auth_callback, callback_url)
            url = spotify.api.authorize_user(callback_url)

            httpServer.start()
            webbrowser.open(url)
            httpServer.join()

        def on_start_recording():
            self.start_recording.configure(state='disabled')
            self.stop_recording.configure(state='normal')

        def on_stop_recording():
            self.stop_recording.configure(state='disabled')
            self.start_recording.configure(state='normal')

        def on_app_close():
            self.processor.stop()
            self.destroy()

        self.protocol("WM_DELETE_WINDOW", on_app_close)
        self.title("Spotify EEG Data Collection")

        self.control_frame = tk.Frame(self)
        self.control_frame.pack()

        self.like = tk.Button(self.control_frame, text="Like", bg="green")
        self.like.pack(side=tk.LEFT)

        self.meh = tk.Button(self.control_frame, text="Meh", bg="grey")
        self.meh.pack(side=tk.LEFT)

        self.dislike = tk.Button(self.control_frame, text="Dislike", bg="red")
        self.dislike.pack(side=tk.LEFT)

        self.app_frame = tk.Frame(self)
        self.app_frame.pack()

        self.start_recording = tk.Button(self.app_frame, text="Record", command=on_start_recording)
        self.start_recording.pack(side=tk.LEFT)

        self.stop_recording = tk.Button(self.app_frame, text="Stop recording", command=on_stop_recording, state='disabled')
        self.stop_recording.pack(side=tk.LEFT)

        self.connect_to_spotify = tk.Button(self.app_frame, text="Connect Spotify", command=on_connect_to_spotify)
        self.connect_to_spotify.pack(side=tk.LEFT)

        self.response_field = widgets.TextArea(self, height=10)
        self.response_field.pack()

        self.song_progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=500, mode="determinate")
        self.song_progress.pack()

        self.figure = pyplot.Figure()
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack()
        self.ani = animation.FuncAnimation(self.figure, self.draw, interval=100)

        self.after(1000, self.periodic_update)

        self.processor = ProcessorThread()
        self.processor.start()

    def draw(self, event):
        global DATA_Y
        global DATA_X
        self.ax.clear()
        self.ax.plot(DATA_Y, DATA_X)
        self.ax.title.set_text("{} sec".format(datetime.now()))

    def periodic_update(self):
        """ 
        """
        if hasattr(configuration, "TOKEN"):
            info = get_playback_info(configuration.TOKEN)

            text = "\n".join([f"{key: <10} = {value: <20}" for key, value in info.items()])
            self.response_field.set_text(text)

            progress = (info["progress"] / info["duration"]) * 100
            self.song_progress["value"] = progress

        self.after(1000, self.periodic_update)


if __name__ == '__main__':
    app = GuiApp()
    app.mainloop()

