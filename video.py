import tkinter as tk
from tkvideoplayer import TkinterVideo
from tkinter.filedialog import asksaveasfilename
import os
import json
from copy import deepcopy
from PIL import Image, ImageTk
from cropper import get_bounding_boxes


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
        self.video_player.bind_all('<<Duration>>', self.update_slider)
        self.video_player.bind_all('<<SecondChanged>>', self.update_slider_pos)

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

        self.last_note_images = []  # ImageTK
        with open('notes.json') as f:  # [{'r': [] ...}, {'r': [] ...} ...]
            self.notes = json.load(f)

        # get_bounding_boxes()

        self.history = []

        self.play_pause_button = tk.Button(self, text='Play', command=self.play_pause)
        self.play_pause_button.grid(row=10, column=3, sticky='news', padx=3, pady=3)

        self.slider_value = tk.IntVar()
        self.progress_slider = tk.Scale(self, variable=self.slider_value, from_=0, to=0, orient='horizontal', command=self.seek)
        self.progress_slider.grid(row=10, column=4, sticky='news', padx=3, pady=3, columnspan=5)

        self.speed_var = tk.StringVar(self, '1x')
        self.speed_dropdown = tk.OptionMenu(self, self.speed_var, '1x', '0.5x', '0.25x', '0.125x', '0.0625x', '0.02x')
        self.speed_dropdown.grid(row=10, column=9, sticky='news', padx=3, pady=3)

        # Voice input buttons

        self.voice_input_options = tk.Frame(self, background='grey', width=384, height=280)
        self.voice_input_options.grid(row=11, column=0, rowspan=6, columnspan=3)

        self.rh_on = tk.IntVar()
        self.lh_on = tk.IntVar()
        self.symbol_on = tk.IntVar()
        self.extra_on = tk.IntVar()
        
        self.check_box_frame = tk.Frame(self)
        self.check_box_frame.grid(row=11, column=0, rowspan=1, columnspan=1)
        self.rh_check_box = tk.Checkbutton(self.check_box_frame, text='RH', variable=self.rh_on, onvalue=1, offvalue=0)
        self.rh_check_box.pack()
        self.lh_check_box = tk.Checkbutton(self.check_box_frame, text='LH', variable=self.lh_on)
        self.lh_check_box.pack()
        self.symbol_check_box = tk.Checkbutton(self.check_box_frame, text='Symbol', variable=self.symbol_on)
        self.symbol_check_box.pack()
        self.extra_check_box = tk.Checkbutton(self.check_box_frame, text='Extra', variable=self.extra_on)
        self.extra_check_box.pack()

        self.fast_place_frame = tk.Frame(self)
        self.fast_place_frame.grid(row=12, column=0)
        self.fast_place_label = tk.Label(self.fast_place_frame, text='Fast place command')
        self.fast_place_label.pack()
        self.fast_place_text = tk.Text(self.fast_place_frame, width=10, height=1)
        self.fast_place_text.pack()
        self.fast_place_button = tk.Button(self.fast_place_frame, text='Enter', command=self.fast_place)
        self.fast_place_button.pack()

        # -----

        self.animation_duration = 0.1

        self.duration_frame = tk.Frame(self)
        self.duration_frame.grid(row=12, column=1)
        self.duration_label = tk.Label(self.duration_frame, text='Animation duration (sec)')
        self.duration_label.pack()
        self.duration_text = tk.Text(self.duration_frame, width=10, height=1)
        self.duration_text.pack()
        self.duration_button = tk.Button(self.duration_frame, text='Enter', command=self.get_animation_duration)
        self.duration_button.pack()

        with open('misc.json') as f:
            self.misc_data = json.load(f)
            self.misc_data.setdefault('guidelines', [])
            self.misc_data.setdefault('pagebreaks', [])

        if len(self.notes) <= len(self.misc_data['pagebreaks']):
            self.create_new_page()

        self.place_frame = tk.Frame(self)
        self.place_frame.grid(row=11, column=1)
        self.place_note_button = tk.Button(self.place_frame, text='Place voice', command=self.place_voice_button)
        self.place_note_button.pack(fill='both')
        self.place_guideline_button = tk.Button(self.place_frame, text='Place guideline', command=self.place_guideline)
        self.place_guideline_button.pack()

        self.pagebreak_button = tk.Button(self.place_frame, text='Pagebreak', command=self.place_pagebreak)
        self.pagebreak_button.pack(fill='both')

        self.place_mode = tk.StringVar(self, 'before')
        self.place_mode_menu = tk.OptionMenu(self.place_frame, self.place_mode, 'before', 'on')
        self.place_mode_menu.pack(fill='both')

        self.animation_type = tk.StringVar(self, 'fade')
        self.animation_type_menu = tk.OptionMenu(self.place_frame, self.animation_type, 'fade', 'glow', 'slide', 'drop')
        self.animation_type_menu.pack(fill='both')

        self.save_clear_frame = tk.Frame(self)
        self.save_clear_frame.grid(row=13, column=1)
        self.save_button = tk.Button(self.save_clear_frame, text='Save Notes', command=self.save_json)
        self.save_button.pack()
        self.clear_button = tk.Button(self.save_clear_frame, text='Clear page', command=self.clear)
        self.clear_button.pack()

        self.undo_button = tk.Button(self, text='Undo', command=self.undo, state=tk.DISABLED)
        self.undo_button.grid(row=13, column=0)

        # Voice input

        self.voice_input_canvas = tk.Canvas(self, width=896, height=280, background='#1f2947')
        self.voice_input_canvas.grid(row=11, column=3, rowspan=3, columnspan=10)

        self.view_width = 5  # 5 seconds

        self.voice_input_items = []  # All items in canvas

        self.playback_line = None
        self.playback_elements = []
        self.update_voice_input(event=None)

        self.set_notes(1, 'extra', 0.5, None, None)

    def set_notes(self, page, voice, new_duration, direction, shift):
        voice_notes = self.notes[page - 1][voice]
        for i, note in enumerate(voice_notes):
            self.notes[page - 1][voice][i]['duration'] = new_duration
            if direction:
                if direction == 'back':
                    self.notes[page - 1][voice][i]['timing'] -= shift
                if direction == 'forward':
                    self.notes[page - 1][voice][i]['timing'] += shift

        with open('notes.json', 'w') as f:
            json.dump(self.notes, f)

    def create_new_page(self):
        new_page = {
            'r': [], 'l': [], 'symbols': [], 'extra': []
        }
        self.notes.append(new_page)

    def undo(self):
        recent = self.history[-1]
        self.notes = recent
        self.update_note_viewer()
        self.update_voice_input(event=None)
        self.history.remove(recent)

        if not self.history:
            self.undo_button.configure(state=tk.DISABLED)

    def clear(self):
        self.notes[-1] = {
            'r': [], 'l': [], 'symbols': [], 'extra': []
        }
        new_guidelines = []
        for line in self.misc_data['guidelines']:
            if line <= self.misc_data['pagebreaks'][-1]:
                new_guidelines.append(line)
        self.misc_data['guidelines'] = new_guidelines
        with open('notes.json', 'w') as f:
            json.dump(self.notes, f)
        with open('misc.json', 'w') as f:
            json.dump(self.misc_data, f)

        self.update_note_viewer()
        self.update_voice_input(event=None)

    def fast_place(self):
        text = self.fast_place_text.get("1.0", 'end-1c')
        split_hyphens = text.split('-')
        if len(split_hyphens) == 3:
            try:
                start_guideline_idx = int(split_hyphens[0]) - 1
                end_guideline_idx = int(split_hyphens[1]) - 1
                num_notes = int(split_hyphens[2])

                if start_guideline_idx < end_guideline_idx < len(self.misc_data['guidelines']):
                    start_duration = self.misc_data['guidelines'][start_guideline_idx]
                    graduation = (self.misc_data['guidelines'][end_guideline_idx] - start_duration) / num_notes
                    for i in range(num_notes):
                        duration = start_duration + i * graduation
                        self.place_voice(duration)

            except ValueError:
                return

    def get_animation_duration(self):
        text = self.duration_text.get("1.0", 'end-1c')
        try:
            float_value = float(text)
            self.animation_duration = float_value
        except ValueError:
            self.animation_duration = 0.1
        print(self.animation_duration)

    def save_json(self):
        filepath = asksaveasfilename(defaultextension='.json', initialdir='./', filetypes=(("JSON", "*.json"),))
        print(filepath)
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(self.notes, f)

    def update_slider_pos(self, event):
        self.slider_value.set(int(self.video_player.current_duration()))

    def update_slider(self, event):
        duration = self.video_player.video_info()["duration"]
        self.progress_slider["to"] = duration

    def seek(self, a):
        self.video_player.seek(self.slider_value.get())

    def play_pause(self):
        if self.video_player.is_paused():
            self.video_player.play(float(self.speed_var.get().replace('x', '')))
            self.play_pause_button['text'] = 'Pause'
        else:
            self.video_player.pause()
            self.play_pause_button['text'] = 'Play'

    def update_note_viewer(self):
        for image in self.last_note_images:
            self.note_viewer.delete(image)
        self.last_note_images = []

        for voice, notes in self.notes[self.page - 1].items():
            if notes:
                note_id = len(notes)
                filepath = ''
                if voice == 'r':
                    filepath = f'Notes/Page{self.page}/RH/r{note_id}.png'
                if voice == 'l':
                    filepath = f'Notes/Page{self.page}/LH/l{note_id}.png'
                if voice == 'symbols':
                    filepath = f'Notes/Page{self.page}/Symbols/s{note_id}.png'
                if voice == 'extra':
                    filepath = f'Notes/Page{self.page}/Extra/e{note_id}.png'

                if os.path.isfile(filepath):
                    img_data = Image.open(filepath).convert("RGBA")

                    r, g, b, a = img_data.split()
                    if voice == 'r':  # Red
                        r = r.point(lambda i: i + 200)
                    if voice == 'l':  # Yellow
                        r = r.point(lambda i: i + 200)
                        g = g.point(lambda i: i + 200)
                    if voice == 'symbols':
                        g = g.point(lambda i: i + 200)
                    if voice == 'extra':
                        b = b.point(lambda i: i + 200)
                    new_image = Image.merge('RGBA', (r, g, b, a))

                    scaled_img_data = new_image.resize((384, 440))
                    tk_image = ImageTk.PhotoImage(scaled_img_data)

                    self.last_note_images.append(tk_image)

        for image in self.last_note_images:
            self.note_viewer.create_image(0, 0, anchor='nw', image=image)

    def check_note_placeable(self, note, voice):
        # Can't be before an existing note or on an existing note
        if self.notes[self.page - 1][voice]:
            last_note = self.notes[self.page - 1][voice][-1]
            if note['timing'] > last_note['timing']:
                return True
            else:
                return False
        else:  # No notes
            return True

    def place_voice_button(self):
        current_frame = self.video_player.current_duration()
        self.place_voice(current_frame)

    def place_voice(self, duration):
        timing = duration if self.place_mode.get() == 'on' else duration - self.animation_duration
        new_note = {'timing': timing, 'animation': self.animation_type.get(), 'duration': self.animation_duration}

        placeable_voices = []

        if self.rh_on.get() and self.check_note_placeable(new_note, 'r'):
            placeable_voices.append('r')
        if self.lh_on.get() and self.check_note_placeable(new_note, 'l'):
            placeable_voices.append('l')
        if self.symbol_on.get() and self.check_note_placeable(new_note, 'symbols'):
            placeable_voices.append('symbols')
        if self.extra_on.get() and self.check_note_placeable(new_note, 'extra'):
            placeable_voices.append('extra')
        if not (self.rh_on.get() or self.lh_on.get() or self.symbol_on.get() or self.extra_on.get()):
            return

        for voice in placeable_voices:
            self.history.append(deepcopy(self.notes))
            self.notes[self.page - 1][voice].append(new_note)
            self.undo_button.configure(state=tk.ACTIVE)

        with open('notes.json', 'w') as f:
            json.dump(self.notes, f)

        self.update_note_viewer()
        self.update_voice_input(event=None)

    def place_guideline(self):
        current_duration = self.video_player.current_duration()
        can_place = False

        if self.misc_data['guidelines']:
            if current_duration > self.misc_data['guidelines'][-1]:
                can_place = True
        else:
            can_place = True

        if can_place:
            self.misc_data['guidelines'].append(current_duration)
            with open('misc.json', 'w') as f:
                json.dump(self.misc_data, f)

        self.update_voice_input(event=None)

    def place_pagebreak(self):
        current_duration = self.video_player.current_duration()
        can_place = False

        if self.misc_data['pagebreaks']:
            if current_duration > self.misc_data['pagebreaks'][-1]:
                can_place = True
        else:
            can_place = True

        if can_place:
            self.misc_data['pagebreaks'].append(current_duration)
            with open('misc.json', 'w') as f:
                json.dump(self.misc_data, f)

        if len(self.notes) <= len(self.misc_data['pagebreaks']):
            self.create_new_page()
        self.update_voice_input(event=None)

    def update_voice_input(self, event):
        current_duration = self.video_player.current_duration()
        left_frame = (current_duration // self.view_width) * self.view_width
        playback_rel_x = (current_duration % self.view_width) / self.view_width

        # Get the page number
        max_idx = 0
        for i, page_break in enumerate(self.misc_data['pagebreaks']):
            if current_duration > page_break:
                max_idx = i + 1
        if max_idx + 1 != self.page:  # Page has changed
            self.page = max_idx + 1
            self.note_viewer_image = self.note_viewer.create_image(0, 0, anchor='nw',
                                                                   image=self.page_imgs[self.page - 1])

        self.voice_input_items = []  # Clear everything

        self.voice_input_canvas.delete('playback_line')
        self.playback_line = self.voice_input_canvas.create_line(playback_rel_x * 896, 0, playback_rel_x * 896, 280, fill='yellow', tags='playback_line')
        self.voice_input_items.append(self.playback_line)

        # header = self.voice_input_canvas.create_rectangle(0, 0, 896, 25, fill='black', tags='header')
        # self.voice_input_items.append(header)

        self.voice_input_canvas.delete('note')

        for page in self.notes:
            for voice, notes in page.items():
                for note in notes:
                    x_val = (note['timing'] - left_frame) / self.view_width
                    y_val = 0
                    colour = 'red'
                    if voice == 'l':
                        y_val = 1
                        colour = 'yellow'
                    elif voice == 'symbols':
                        y_val = 2
                        colour = 'green'
                    elif voice == 'extra':
                        y_val = 3
                        colour = 'blue'

                    new_circle = self.voice_input_canvas.create_oval(x_val * 896 - 5, 20 + 255 / 8 + y_val * (255 / 4),
                                                                     x_val * 896 + 5, 30 + 255 / 8 + y_val * (255 / 4), fill=colour, tags='note', outline='white')
                    self.voice_input_items.append(new_circle)

                    fade_line = self.voice_input_canvas.create_line(x_val * 896, 25 + 255 / 8 + y_val * (255 / 4),
                                                                    (x_val + note['duration'] / self.view_width) * 896, 25 + 255 / 8 + y_val * (255 / 4), fill='white', tags='note')
                    self.voice_input_items.append(fade_line)

        self.voice_input_canvas.delete('guideline')

        for i, duration in enumerate(self.misc_data['guidelines']):
            x_val = (duration - left_frame) / self.view_width
            new_line = self.voice_input_canvas.create_line(x_val * 896, 0, x_val * 896, 280, fill='grey', tags='guideline')
            self.voice_input_items.append(new_line)

            line_text = self.voice_input_canvas.create_text(x_val * 896, 260, anchor='sw', text=str(i + 1), fill='grey', tags='guideline', font='Arial 10')
            self.voice_input_items.append(line_text)

        self.voice_input_canvas.delete('pagebreak')

        for i, duration in enumerate(self.misc_data['pagebreaks']):
            x_val = (duration - left_frame) / self.view_width
            new_line = self.voice_input_canvas.create_line(x_val * 896, 0, x_val * 896, 280, fill='cyan', dash=(5, 1),
                                                           tags='pagebreak')
            self.voice_input_items.append(new_line)

            line_text = self.voice_input_canvas.create_text(x_val * 896, 260, anchor='se', text=str(i + 1), fill='cyan',
                                                            tags='pagebreak', font='Arial 10')
            self.voice_input_items.append(line_text)

"""
TODO:

Add guideline tool
Add fast notes tool, select amount of notes to put
"""