import tkinter as tk

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


def draw(_, data, subplot, canvas):
    subplot.clear()
    subplot.plot(DATA_Y, DATA_X)
    canvas.draw()
    pyplot.title("{} sec".format(datetime.now()))


class GuiApp:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("EEG Music Preferences Data Collection Interface")

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
            self.processor.stop()
            self.window.quit()

        self.window.protocol("WM_DELETE_WINDOW", on_app_close)

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

        # Signal plot canvas setup
        self.figure = pyplot.Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
        self.canvas.get_tk_widget().pack()
        self.ani = animation.FuncAnimation(self.figure, draw, fargs=(DATA_X, self.ax, self.canvas), interval=100)
        self.processor = ProcessorThread()

    def run(self):
        self.processor.start()
        self.window.mainloop()



if __name__ == '__main__':
    gui = GuiApp()
    gui.run()
