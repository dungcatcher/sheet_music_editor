import tkinter as tk
import mido


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
        self.note_id_rectangle = self.canvas.create_rectangle(0, 0, 50, 540, fill='#474747')
        self.canvas.grid(row=2, column=0, rowspan=6, columnspan=12)

        self.view_height = 20  # 20 notes
        self.view_width = 5  # 5 seconds
        self.view_x_offset = 0
        self.view_y_offset = 30  # Lowest note

    def update_canvas(self):
        for note_id in range(self.view_y_offset, self.view_y_offset + self.view_height):
            # self.canvas.create_text()

            if note_id % 2 == 0:
                colour = '#9c9c9c'
            else:
                colour = '#bab8b8'



