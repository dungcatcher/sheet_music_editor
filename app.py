import tkinter as tk
from sheet_music import SheetMusic
from midi import MidiEditor
from video import VideoEditor


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")

        self.frames = {}
        for frame in [SheetMusic, MidiEditor, VideoEditor]:
            new_frame = frame(self)
            self.frames[frame.name] = new_frame  # Initialise every frame
        # self.show_frame('sheetmusic')

        self.options_frame = tk.Frame(self, width=200, height=200)
        self.options_frame.pack(fill='both')

        self.video_button = tk.Button(self.options_frame, text='Video Editor', command=lambda: self.show_frame('video'))
        self.video_button.pack()
        self.sheet_button = tk.Button(self.options_frame, text='Sheet Editor', command=lambda: self.show_frame('sheetmusic'))
        self.sheet_button.pack()

    def show_frame(self, frame_id):
        self.options_frame.pack_forget()
        frame = self.frames[frame_id]
        for f_id, f in self.frames.items():
            if f_id != frame_id:
                f.pack_forget()
        frame.grid(row=0, column=0)


