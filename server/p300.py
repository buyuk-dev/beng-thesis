""" 2021 Created by michal@buyuk-dev.com
"""

import tkinter as tk
import random

from server.markers import MarkerStream


class OddballApp:
    def __init__(self, ntrials=100):
        """Create task window."""

        # Root window
        self.root = tk.Tk()
        self.root.geometry("800x400")

        # Button label
        self.text = tk.StringVar()
        self.text.set("start")

        # Button
        self.btn = tk.Button(
            self.root,
            textvariable=self.text,
            bg="lightgrey",
            fg="black",
            width=800,
            height=400,
        )
        self.btn["font"] = ("times", 300, "bold")
        self.btn.config(command=lambda: self.click())
        self.btn.pack()

        # Experiment parameters
        self.trials_counter = 0
        self.max_trials = ntrials
        self.event_duration = 500
        self.pause_duration = 1000
        self.event_stream = []

        # Generate random stream of events (letters) to show.
        events = list("ABCDE")
        while len(self.event_stream) < self.max_trials:
            random.shuffle(events)
            self.event_stream.extend(events)

        # Marker stream
        self.marker_stream = MarkerStream(events)
        self.marker_stream.markers.append("stop")
        self.marker_stream.markers.append("start")

    def pause(self):
        """Break between the trials."""
        if self.trials_counter == self.max_trials:
            self.marker_stream.push("stop")
            return

        self.text.set("")
        self.root.after(self.pause_duration, lambda: self.show_letter())

    def show_letter(self):
        """Random trial: show next letter from the stream."""
        event = self.event_stream[self.trials_counter]
        self.trials_counter += 1
        self.text.set(event)
        self.marker_stream.push(event)
        self.root.after(self.event_duration, lambda: self.pause())

    def click(self):
        """Start the task."""
        self.marker_stream.push("start")
        self.pause()

    def run(self):
        """Show window."""
        self.root.mainloop()


if __name__ == "__main__":
    app = OddballApp(ntrials=10)
    app.run()
