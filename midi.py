import tkinter as tk
import mido
from mido import MidiFile


def midi_note_to_scientific(note_num):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    scientific = ''
    mod = note_num % 12
    scientific += notes[mod]

    scientific += str(note_num // 12 - 1)

    return scientific


def parse_notes(file):
    mid = MidiFile(file, clip=True)

    started_notes = []

    for track in mid.tracks:
        ticks = 0
        for message in track:
            ticks += message.time
            if message.type == 'note_on':
                proto_note_dict = {
                    'note': message.note,
                    'vel': message.velocity,
                    'start': ticks
                }
                started_notes.append(proto_note_dict)

    print(started_notes)


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
        self.note_id_rectangle = self.canvas.create_rectangle(0, 0, 50, 540, fill='lightgrey')
        self.canvas.grid(row=2, column=0, rowspan=6, columnspan=12)

        self.canvas.bind_all("<Shift-MouseWheel>", self.horizontal_scroll)

        self.view_height = 40  # 20 notes
        self.view_width = 5  # 5 seconds
        self.view_x_offset = 0
        self.view_y_offset = 30  # Lowest note

        self.init_canvas()

        parse_notes('song.mid')

    def init_canvas(self):
        for note_id in range(self.view_y_offset, self.view_y_offset + self.view_height):
            y_val = self.view_height - (note_id - self.view_y_offset)
            row_height = int(540 / self.view_height)
            note_text = midi_note_to_scientific(note_id)
            self.canvas.create_text(25, (y_val - 0.5) * row_height, anchor='center', text=note_text, font='Arial 8')

            if note_id % 2 == 0:
                colour = '#404258'
            else:
                colour = '#474e68'
            self.canvas.create_rectangle(50, (y_val - 1) * row_height, 1280, y_val * row_height, fill=colour, outline='')

    def horizontal_scroll(self, event):
        x_scroll = -(event.delta // 120)
        self.view_x_offset += x_scroll * 0.25
        if self.view_x_offset < 0:
            self.view_x_offset = 0
        print(self.view_x_offset)


