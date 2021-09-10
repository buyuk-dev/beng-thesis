import tkinter as tk
import tkinter.ttk as ttk


class TextArea(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_text(self, text):
        self.delete(1.0, tk.END)
        self.insert(tk.INSERT, text)


class SongInfo(tk.Frame):
    def __init__(self, root, height, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.info_text = TextArea(self, height=height)
        self.info_text.pack(fill="x")

        self.progress_bar = ttk.Progressbar(
            self, orient=tk.HORIZONTAL, mode="determinate"
        )
        self.progress_bar.pack(fill="x")

    def update(self, playback_info):
        if playback_info is not None:
            info = self._format(playback_info)
            progress = playback_info["progress"]
            duration = playback_info["duration"]
            percentage = progress / duration * 100

            self.info_text.set_text(info)
            self.progress_bar["value"] = percentage

    def _format(self, playback_info):
        return "\n".join(
            [f"{key: <10} = {value: <20}" for key, value in playback_info.items()]
        )
