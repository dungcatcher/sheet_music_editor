import tkinter as tk
from tkvideoplayer import TkinterVideo
import os
from PIL import Image, ImageTk


class VideoEditor(tk.Frame):
    name = 'video'

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Format grids
        for c in range(10):
            self.columnconfigure(c, weight=1)
        for r in range(17):
            self.rowconfigure(r, weight=1)

        self.video_frame = tk.Frame(self, background='grey', width=896, height=400)
        self.video_frame.grid(row=0, column=3, rowspan=10, columnspan=7)

        self.video_player = TkinterVideo(master=self, consistant_frame_rate=True)
        self.video_player.load('Volodos_Edited.mp4')
        self.video_player.grid(row=0, column=3, rowspan=10, columnspan=7, sticky='nsew')
        self.video_player.bind_all('<<FrameGenerated>>', self.update_voice_input)

        self.video_options = tk.Frame(self, background='lightgrey', width=896, height=40)
        self.video_options.grid(row=10, column=3, rowspan=1, columnspan=7)

        self.note_viewer = tk.Canvas(self, width=384, height=440)
        self.note_viewer.grid(row=0, column=0, columnspan=3, rowspan=11)

        # Load images
        self.page_imgs = []
        for file in sorted(os.listdir('Score/Raw/'), key=lambda x: int(x.split('.png')[0])):
            filepath = f'Score/Raw/{file}'
            img_data = Image.open(filepath).convert("L")
            scaled_img_data = img_data.resize((384, 440))
            tk_image = ImageTk.PhotoImage(scaled_img_data)
            self.page_imgs.append(tk_image)

        self.page = 1
        self.note_viewer_image = self.note_viewer.create_image(0, 0, anchor='nw', image=self.page_imgs[self.page - 1])

        self.last_note_image = None  # ImageTK
        self.notes = []  # List of notes {'voice', 'number', 'animation', 'duration'}

        # self.update_note_viewer()
        # self.note_viewer.create_image(0, 0, anchor='nw', image=self.last_note_image)

        self.play_pause_button = tk.Button(self, text='Play', command=self.play_pause)
        self.play_pause_button.grid(row=10, column=3, sticky='news', padx=3, pady=3)

        self.back_frame_button = tk.Button(self, text='Back Frame')
        self.back_frame_button.grid(row=10, column=4, sticky='news', padx=3, pady=3)

        # Voice input buttons

        self.voice_input_options = tk.Frame(self, background='grey', width=384, height=440)
        self.voice_input_options.grid(row=11, column=0, rowspan=7, columnspan=3)

        self.rh_on = tk.IntVar()
        self.lh_on = tk.IntVar()
        self.symbol_on = tk.IntVar()

        self.rh_check_box = tk.Checkbutton(self, text='RH', variable=self.rh_on, onvalue=1, offvalue=0)
        self.rh_check_box.grid(row=11, column=0)

        self.lh_check_box = tk.Checkbutton(self, text='LH', variable=self.lh_on)
        self.lh_check_box.grid(row=12, column=0)

        self.symbol_check_box = tk.Checkbutton(self, text='Symbol', variable=self.symbol_on)
        self.symbol_check_box.grid(row=13, column=0)

        self.place_note_button = tk.Button(self, text='Place Voice', command=self.place_voice)
        self.place_note_button.grid(row=11, column=1)

        # Voice input

        self.voice_input_canvas = tk.Canvas(self, width=896, height=280, background='#1f2947')
        self.voice_input_canvas.grid(row=11, column=3, rowspan=3, columnspan=10)

        self.view_width = 50  # 50 frames

        self.playback_line = None
        self.playback_elements = []
        self.update_voice_input(event=None)

    def play_pause(self):
        if self.video_player.is_paused():
            self.video_player.play(0.5)
            self.play_pause_button['text'] = 'Pause'
        else:
            self.video_player.pause()
            self.play_pause_button['text'] = 'Play'

    def update_note_viewer(self):
        last_note = self.notes[-1]
        filepath = None

        if last_note['voice'] == 'r':
            filepath = f'Notes/Page {self.page}/RH/r{last_note["number"]}.png'
        if last_note['voice'] == 'l':
            filepath = f'Notes/Page {self.page}/LH/l{last_note["number"]}.png'
        if last_note['voice'] == 'symbol':
            filepath = f'Notes/Page {self.page}/Symbols/s{last_note["number"]}.png'

        if os.path.isfile(filepath):
            img_data = Image.open(filepath).convert("RGBA")
            # Turn red
            img_pixels = img_data.getdata()
            new_img = []
            for pixel in img_pixels:
                if pixel != (255, 255, 255, 0):
                    new_img.append((255, 0, 0, 255))
                else:
                    new_img.append(pixel)
            img_data.putdata(new_img)
            scaled_img_data = img_data.resize((384, 440))
            tk_image = ImageTk.PhotoImage(scaled_img_data)
            self.last_note_image = tk_image
            self.note_viewer.create_image(0, 0, anchor='nw', image=self.last_note_image)

    def place_voice(self):
        current_frame = self.video_player.current_frame_number()
        if self.rh_on.get():
            new_note = {'voice': 'r', 'number': current_frame, 'animation': 'fade', 'duration': 2}
            print(new_note)
            self.notes.append(new_note)
        if self.lh_on.get():
            new_note = {'voice': 'l', 'number': current_frame, 'animation': 'fade', 'duration': 2}
            self.notes.append(new_note)
        if self.symbol_on.get():
            new_note = {'voice': 'symbol', 'number': current_frame, 'animation': 'fade', 'duration': 2}
            self.notes.append(new_note)
        if not (self.rh_on.get() or self.lh_on.get() or self.symbol_on.get()):
            return

        self.update_note_viewer()
        self.update_voice_input(event=None)

    def update_voice_input(self, event):
        current_frame = self.video_player.current_frame_number()
        left_frame = (current_frame // self.view_width) * self.view_width
        playback_rel_x = (current_frame % self.view_width) / self.view_width

        self.voice_input_canvas.delete(self.playback_line)
        self.playback_line = self.voice_input_canvas.create_line(playback_rel_x * 896, 0, playback_rel_x * 896, 280, fill='yellow')

        for element in self.playback_elements:
            self.voice_input_canvas.delete(element)
        header = self.voice_input_canvas.create_rectangle(0, 0, 896, 25, fill='black')
        self.playback_elements.append(header)
        for i in range(6):
            x_val = i * 150
            text = self.voice_input_canvas.create_text(x_val, 12, fill='white', anchor='center')
            self.playback_elements.append(text)
