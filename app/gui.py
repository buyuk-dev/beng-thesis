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

import spotify

DATA_X = [0] * 100
DATA_Y = list(range(100))
INFO_TEXT = ""

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
        self.s.bind(("localhost", 5000))

        while not self.stopped():
            self.s.listen(1)
            print('Listening on port 5000 ...')
            client, address = self.s.accept()
            request = client.recv(1024).decode()
            print(request)
            client.close()


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
            code, playback_info = spotify.get_current_playback_info(resp["access_token"])

            filtered = {}
            filtered["artistis"] = playback_info["item"]["artists"][0]["name"]
            filtered["song"] = playback_info["item"]["name"]
            filtered["popularity"] = playback_info["item"]["popularity"]
            filtered["album"] = playback_info["item"]["album"]["name"]
            filtered["released"] = playback_info["item"]["album"]["release_date"]

            global INFO_TEXT
            INFO_TEXT = pprint.pformat(filtered, indent=4)

        self.server.run()



def draw(_, data, subplot, canvas):
    subplot.clear()
    subplot.plot(DATA_Y, DATA_X)
    canvas.draw()
    pyplot.title("{} sec".format(datetime.now()))


class GuiApp:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("EEG Music Preferences Data Collection Interface")

        url = spotify.authorize_user("http://localhost:5000/callback")
        webbrowser.open(url)

        def on_like():
            print("Signal: +1")

        def on_neutral():
            print("Signal: 0")

        def on_dislike():
            print("Signal: -1")

        def on_start_recording():
            self.start_recording.configure(state='disabled')
            self.stop_recording.configure(state='normal')
            print("Recording started")


        def on_stop_recording():
            self.stop_recording.configure(state='disabled')
            self.start_recording.configure(state='normal')
            print("Recording stopped")

        def on_app_close():
            self.httpServer.stop()
            self.processor.stop()
            self.window.destroy()

        def periodic_update(text):
            global INFO_TEXT
            text.delete(1.0, tk.END)
            text.insert(tk.INSERT, INFO_TEXT)
            self.window.after(1000, periodic_update, self.response_field)

        # Buttons setup
        self.control_frame = tk.Frame(self.window)
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

        self.response_field = tk.Text(self.window)
        self.response_field.pack()

        # Signal plot canvas setup
        self.figure = pyplot.Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
        self.canvas.get_tk_widget().pack()
        self.ani = animation.FuncAnimation(self.figure, draw, fargs=(DATA_X, self.ax, self.canvas), interval=100)
        self.processor = ProcessorThread()
        #self.httpServer = ServerThread()
        self.httpServer = SpotifyCallbackThread()

        self.window.protocol("WM_DELETE_WINDOW", on_app_close)
        self.window.after(1000, periodic_update, self.response_field)

    def run(self):
        self.httpServer.start()
        self.processor.start()
        self.window.mainloop()


if __name__ == '__main__':
    #server = SpotifyCallbackThread()
    #server.start()
    gui = GuiApp()
    gui.run()

