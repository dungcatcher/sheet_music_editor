import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
from PIL import Image, ImageTk
from note_remover import remove_notes, remove_stave


def handle_selection_area(selection1, selection2):
    sorted_x = sorted([selection1[0], selection2[0]])
    sorted_y = sorted([selection1[1], selection2[1]])
    return (sorted_x[0], sorted_y[0]), (sorted_x[1], sorted_y[1])


class SheetMusic(tk.Frame):
    name = 'sheetmusic'

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Format grids
        for c in range(8):
            self.columnconfigure(c, weight=1)
        for r in range(12):
            self.rowconfigure(r, weight=1)

        self.options_frame = tk.Frame(self, background='grey', width=480, height=720)
        self.options_frame.grid(row=0, column=0, rowspan=12, columnspan=3)

        self.label = tk.Label(self, text='Options', font='Arial 20')
        self.label.grid(row=0, column=1)

        self.mode = tk.StringVar(self, "remover")
        self.remove_radio_button = tk.Radiobutton(self, text='Remover', variable=self.mode, value='remover',
                                                  command=self.switch_modes)
        self.remove_radio_button.grid(row=1, column=0, sticky='w', padx=10)

        self.move_radio_button = tk.Radiobutton(self, text='Move tool', variable=self.mode, value='move',
                                                command=self.switch_modes)
        self.move_radio_button.grid(row=2, column=0, sticky='w', padx=10)

        self.save_button = tk.Button(self, text='Save', command=self.save, state=tk.DISABLED)
        self.save_button.grid(row=3, column=0, sticky='w', padx=10)

        self.choose_file_button = tk.Button(self, text='Choose file', command=self.load)
        self.choose_file_button.grid(row=4, column=0, sticky='w', padx=10)

        self.x_thresh_var = tk.IntVar(self, 300)
        self.x_thresh_scale = tk.Scale(self, variable=self.x_thresh_var, orient=tk.HORIZONTAL, from_=0, to=500, label='x threshold')
        self.x_thresh_scale.grid(row=1, column=1, sticky='ew', padx=10, pady=10)

        self.y_thresh_var = tk.IntVar(self, 150)
        self.y_thresh_scale = tk.Scale(self, variable=self.y_thresh_var, orient=tk.HORIZONTAL, from_=0, to=300, label='y threshold')
        self.y_thresh_scale.grid(row=1, column=2, sticky='ew', padx=10, pady=10)

        self.undo_button = tk.Button(self, text='Undo', command=self.undo, state=tk.DISABLED)
        self.undo_button.grid(row=5, column=0, sticky='w', padx=10)

        self.remove_mode = tk.StringVar(self, 'notes')
        self.remove_mode_dropdown = tk.OptionMenu(self, self.remove_mode, 'notes', 'lines')
        self.remove_mode_dropdown.grid(row=6, column=0, sticky='w', padx=10)

        # ---------- Canvas ---------------

        self.canvas = tk.Canvas(self, background='lightgrey', width=800, height=720)
        self.canvas.grid(row=0, column=3, columnspan=5, rowspan=12)

        self.img_data_history = []
        self.orig_img_data = None
        self.scale_factor = None
        self.img_data = None
        self.img = None

        self.canvas_pos = [0, 0]

        self.canvas_image = None
        self.canvas.bind('<Button-1>', self.handle_canvas_selection)
        self.canvas.bind('<B1-Motion>', self.handle_drag)
        self.canvas.bind('<ButtonRelease-1>', self.handle_drop)

        self.select1 = None
        self.select2 = None
        self.selection_area = None

        self.previous_mouse_pos = None

    def undo(self):
        recent = self.img_data_history[-1]
        self.place_image(recent)
        self.img_data_history.remove(recent)

        if not self.img_data_history:
            self.undo_button.configure(state=tk.DISABLED)

    def place_image(self, raw_image_data):
        self.orig_img_data = raw_image_data
        scale_factor = self.canvas.winfo_width() / raw_image_data.width
        self.img_data = self.orig_img_data.resize((800, int(self.orig_img_data.height * scale_factor)))
        self.img = ImageTk.PhotoImage(self.img_data)
        self.canvas_image = self.canvas.create_image(self.canvas_pos[0], self.canvas_pos[1], anchor='nw',
                                                     image=self.img)

    def load(self):
        file_path = askopenfilename(title='Select File', filetypes=(("PNG", "*.png"),), defaultextension='.png',
                                    initialdir='./Score/Raw')
        if file_path:
            img_data = Image.open(file_path).convert("L")
            self.place_image(img_data)

            self.canvas.move(self.canvas_image, -self.canvas_pos[0], -self.canvas_pos[1])
            self.canvas_pos = [0, 0]

            self.save_button.configure(state=tk.ACTIVE)

    def save(self):
        file_path = asksaveasfilename(title='Select Location', filetypes=(("PNG", "*.png"),), defaultextension='.png',
                                      initialdir='./Score/Output')
        self.orig_img_data.save(file_path, "PNG")

    def switch_modes(self):
        pass

    def handle_drag(self, event):
        if self.mode.get() == 'move' and self.orig_img_data:
            self.canvas.configure(cursor="fleur")
            delta_x, delta_y = (event.x - self.previous_mouse_pos[0], event.y - self.previous_mouse_pos[1])
            self.canvas_pos[0] += delta_x
            self.canvas_pos[1] += delta_y

            self.canvas.move(self.canvas_image, delta_x, delta_y)

            self.previous_mouse_pos = (event.x, event.y)

    def handle_drop(self, event):
        self.canvas.configure(cursor='arrow')

    def handle_canvas_selection(self, event):
        if self.orig_img_data:
            if self.mode.get() == 'remover':
                self.canvas.configure(cursor='tcross')

                rel_x, rel_y = ((event.x - self.canvas_pos[0]) / self.img_data.width, (event.y - self.canvas_pos[1]) / self.img_data.height)
                real_pos = (int(rel_x * self.orig_img_data.width), int(rel_y * self.orig_img_data.height))

                if not self.select1:
                    self.select1 = real_pos
                elif not self.select2:
                    self.select2 = real_pos
                    self.selection_area = handle_selection_area(self.select1, self.select2)

                    self.img_data_history.append(self.orig_img_data)
                    self.undo_button.configure(state=tk.ACTIVE)
                    self.canvas.configure(cursor='watch')
                    if self.remove_mode.get() == 'notes':
                        new_img = remove_notes(self.selection_area, self.orig_img_data, self.x_thresh_var.get(), self.y_thresh_var.get())
                    else:
                        new_img = remove_stave(self.selection_area, self.orig_img_data, self.x_thresh_var.get(), self.y_thresh_var.get())
                    self.place_image(new_img)

                    self.select1 = None
                    self.select2 = None
                    self.selection_area = None
                    self.canvas.configure(cursor='arrow')
            else:
                self.previous_mouse_pos = (event.x, event.y)