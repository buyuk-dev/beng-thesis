import tkinter as tk
import flask
import socket

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
import pprint

import configuration
import spotify

DATA_X = [0] * 100
DATA_Y = list(range(100))


class ProcessorThread(threading.Thread):

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


class SpotifyCallbackThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(SpotifyCallbackThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def stop(self):
        self.s.close()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        """ Listen for callback from spotify with auth code.
            After it arrives parse and request access token.
        """
        self.s.bind(("localhost", 5000))
        self.s.listen(1)

        client, address = self.s.accept()

        request = client.recv(512).decode()
        client.close()

        idx = request.find("HTTP")
        request = request[:idx]
        code_idx = request.find("code=")

        code = request[code_idx:].split("=")[-1].strip()
        code, resp = spotify.request_token(code, "http://localhost:5000/callback")

        configuration.TOKEN = resp["access_token"]


class ServerThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(ServerThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        exit()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):

        self.server = flask.Flask("EegHttpServer")
        self.server.debug = False

        @self.server.route("/callback")
        def authorization_callback():
            """ if authorization request had 'state' argument
                authorization_callback will also have the same argument.
            """
            code = flask.request.args.get("code")
            code, resp = spotify.request_token(code, "http://localhost:5000/callback")
            configuration.TOKEN = resp["access_token"]

        self.server.run()


class TextArea(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def set_text(self, text): 
        self.delete(1.0, tk.END)
        self.insert(tk.INSERT, text)


class GuiApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def on_like():
            if configuration.TOKEN is None: 
                print("Access token not available.")
                return

            code, playback_info = spotify.get_current_playback_info(configuration.TOKEN)
            filtered = {}
            filtered["artistis"] = playback_info["item"]["artists"][0]["name"]
            filtered["song"] = playback_info["item"]["name"]
            filtered["popularity"] = playback_info["item"]["popularity"]
            filtered["album"] = playback_info["item"]["album"]["name"]
            filtered["released"] = playback_info["item"]["album"]["release_date"]
           
            text = pprint.pformat(filtered, indent=4)
            self.response_field.set_text(text)

        def on_neutral():
            pass

        def on_dislike():
            httpServer = SpotifyCallbackThread()
            url = spotify.authorize_user("http://localhost:5000/callback")
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
        self.title("EEG Music Preferences Data Collection Interface")

        # Buttons setup
        self.control_frame = tk.Frame(self)
        self.control_frame.pack()

        self.like = tk.Button(self.control_frame, text="Like", bg="green", command=on_like)
        self.like.pack(side=tk.LEFT)

        self.meh = tk.Button(self.control_frame, text="Meh", bg="grey", command=on_neutral)
        self.meh.pack(side=tk.LEFT)

        self.dislike = tk.Button(self.control_frame, text="Dislike", bg="red", command=on_dislike)
        self.dislike.pack(side=tk.LEFT)

        self.start_recording = tk.Button(self.control_frame, text="Record", command=on_start_recording)
        self.start_recording.pack(side=tk.LEFT)

        self.stop_recording = tk.Button(self.control_frame, text="Stop recording", command=on_stop_recording, state='disabled')
        self.stop_recording.pack(side=tk.LEFT)

        self.response_field = TextArea(self)
        self.response_field.pack()

        # Signal plot canvas setup
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
        print("periodic update...")
        self.after(1000, self.periodic_update)


if __name__ == '__main__':
    app = GuiApp()
    app.mainloop()

