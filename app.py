import tkinter as tk
from sheet_music import SheetMusic
from midi import MidiEditor


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")

        self.frames = {}
        for frame in [SheetMusic, MidiEditor]:
            new_frame = frame(self)
            self.frames[frame.name] = new_frame  # Initialise every frame
        self.show_frame('midi')

    def show_frame(self, frame_id):
        frame = self.frames[frame_id]
        for f_id, f in self.frames.items():
            if f_id != frame_id:
                f.pack_forget()
        frame.grid(row=0, column=0)


