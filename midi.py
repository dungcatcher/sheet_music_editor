import tkinter as tk
import mido
from mido import MidiFile

VOICE_COLOURS = {
    'rh': 'red',
    'lh': 'yellow'
}


def midi_note_to_scientific(note_num):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    scientific = ''
    mod = note_num % 12
    scientific += notes[mod]

    scientific += str(note_num // 12 - 1)

    return scientific


def midi_time_to_real(bpm, ppq, tick):  # In ms
    return tick * (60000 / (bpm * ppq))


def parse_notes(file):
    mid = MidiFile(file, clip=True)

    started_notes = []

    bpm = 120
    ppq = 192

    for track in mid.tracks:
        ticks = 0
        for message in track:
            ticks += message.time
            real_time = midi_time_to_real(bpm, ppq, ticks)
            if message.type == 'note_on':
                proto_note_dict = {
                    'note': message.note,
                    'start': real_time
                }
                started_notes.append(proto_note_dict)

    return started_notes


class MidiEditor(tk.Frame):
    name = 'midi'

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Format grids
        for c in range(12):
            self.columnconfigure(c, weight=1)
        for r in range(8):
            self.rowconfigure(r, weight=1)

        self.navbar = tk.Frame(self, background='grey', width=1280, height=180)
        self.navbar.grid(row=0, column=0, rowspan=2, columnspan=12)

        self.label = tk.Label(self, text='Midi Editor', font='Arial 20')
        self.label.grid(row=0, column=0, columnspan=12)

        self.canvas = self.canvas = tk.Canvas(self, background='lightgrey', width=1280, height=540)
        self.note_id_rectangle = self.canvas.create_rectangle(0, 25, 50, 540, fill='lightgrey')
        self.timestamp_rectangle = self.canvas.create_rectangle(0, 0, 1280, 25, fill='black')
        self.canvas.grid(row=2, column=0, rowspan=6, columnspan=12)

        self.canvas.bind_all("<Shift-MouseWheel>", self.horizontal_scroll)
        self.canvas.bind_all("<Control-MouseWheel>", self.zoom)
        self.canvas.bind_all("<MouseWheel>", self.vertical_scroll)
        self.canvas.bind_all("<Button-1>", self.click)

        self.rh_on = tk.IntVar()
        self.lh_on = tk.IntVar()
        self.rh_button = tk.Checkbutton(self, text='RH', variable=self.rh_on, onvalue=1, offvalue=0)
        self.lh_button = tk.Checkbutton(self, text='LH', variable=self.lh_on, onvalue=1, offvalue=0)
        self.rh_button.grid(row=1, column=0)
        self.lh_button.grid(row=1, column=1)

        self.note_data = {
            "rh": [],  # List of notes {'timing', 'animation', 'duration'}
            "lh": []
        }   # For animation

        self.view_height = 40  # Amount of notes
        self.view_width = 5  # Seconds in view
        self.view_x_offset = 0
        self.view_y_offset = 30  # Lowest note

        self.notes = parse_notes('bach1.midi')
        self.canvas_items = []
        self.canvas_notes = []
        self.init_canvas()

    def init_canvas(self):
        for item in self.canvas_items:
            self.canvas.delete(item)
        self.canvas_items = []

        row_height = int(515 / self.view_height)
        # Background
        for note_id in range(self.view_y_offset, self.view_y_offset + self.view_height):
            y_val = self.view_height - (note_id - self.view_y_offset)

            if note_id % 2 == 0:
                colour = '#404258'
            else:
                colour = '#474e68'
            rect = self.canvas.create_rectangle(50, (y_val - 1) * row_height + 25, 1280, y_val * row_height + 25, fill=colour, outline='')
            self.canvas_items.append(rect)

        # Notes
        for note in self.canvas_notes:
            self.canvas.delete(note)
        self.canvas_notes = []

        for note in self.notes:
            y_val = self.view_height - (note['note'] - self.view_y_offset)
            x_val = ((note['start'] / 1000 - self.view_x_offset) / self.view_width)
            new_note = self.canvas.create_rectangle(x_val * 1230 + 50, (y_val - 1) * row_height + 25, x_val * 1230 + 75,
                                                    y_val * row_height + 25, fill='lightgrey', outline='')
            self.canvas_notes.append(new_note)

        # Text for notes
        for note_id in range(self.view_y_offset, self.view_y_offset + self.view_height):
            y_val = self.view_height - (note_id - self.view_y_offset)
            note_text = midi_note_to_scientific(note_id)
            text = self.canvas.create_text(25, (y_val - 0.5) * row_height + 25, anchor='center', text=note_text,
                                           font='Arial 6')
            self.canvas_items.append(text)

            # For note lines
            for voice_id, voice in self.note_data.items():
                for note in voice:
                    x_rel = (note['timing'] - self.view_x_offset) / self.view_width
                    if 0 <= x_rel <= 1:
                        x_real = 50 + x_rel * 1230
                        colour = VOICE_COLOURS[voice_id]
                        line = self.canvas.create_line(x_real, 25, x_real, 540, width=2, fill=colour)
                        self.canvas_items.append(line)

        self.canvas.tag_raise(self.timestamp_rectangle)
        # Text for timestamps
        for graduation in range(11):
            x_val = 50 + 1230 * (0.1 * graduation)
            if graduation != 0:
                time_text = str(round((graduation * 0.1 * self.view_width) + self.view_x_offset, 2)) + 's'
            else:
                time_text = f'{self.view_x_offset}s'
            text = self.canvas.create_text(x_val, 13, anchor='center', text=time_text, font='Arial 8', fill='white')
            self.canvas_items.append(text)

    def horizontal_scroll(self, event):
        x_scroll = -(event.delta // 120)
        self.view_x_offset += x_scroll * 0.25
        if self.view_x_offset < 0:
            self.view_x_offset = 0
        self.init_canvas()

    def zoom(self, event):
        scroll = -(event.delta // 120)
        self.view_height += scroll
        if self.view_height < 10:
            self.view_height = 10
        if self.view_height > 60:
            self.view_height = 60
        self.init_canvas()

    def vertical_scroll(self, event):
        y_scroll = event.delta // 120
        self.view_y_offset += y_scroll
        if self.view_y_offset < 0:
            self.view_y_offset = 0
        if self.view_y_offset > 150:
            self.view_y_offset = 150
        self.init_canvas()

    def click(self, event):
        x_rel = (event.x - 50) / 1230
        if 0 <= x_rel <= 1:
            time = self.view_x_offset + x_rel * self.view_width
            new_note = {
                'timing': time,
                'animation': 'fade',
                'duration': 2
            }
            if self.rh_on.get():
                self.note_data['rh'].append(new_note)
            if self.lh_on.get():
                self.note_data['lh'].append(new_note)

            self.init_canvas()

