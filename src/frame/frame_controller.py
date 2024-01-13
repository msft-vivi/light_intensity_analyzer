
from . import *

class ControlFrame(tk.Frame):
    def __init__(self, master : tk.Tk, image_frame : 'ImageFrame'):
        # super().__init__(master, relief=tk.RAISED, borderwidth=2, background='green')
        super().__init__(master, relief=tk.RAISED)

        # General setup.
        self.master = master
        self.image_frame = image_frame

        # Widgets setup.
        self.btn_open = tk.Button(master=self, text="Open", command=self.image_frame.load_image)
        self.btn_save = tk.Button(master=self, text="Save As...")

        self.btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=1, column=0, sticky="ew", padx=5)

        self.draw_type = tk.StringVar(self)
        self.draw_type.set("Line")  # default value
        self.draw_type.trace_add("write", self.on_draw_type_change) # type: ignore

        self.draw_type_menu = tk.OptionMenu(self, self.draw_type, "Line", "Rectangle")
        self.draw_type_menu.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    def on_draw_type_change(self, *args : Any):
        self.image_frame.draw_type.set(self.draw_type.get())
        msg = f"Draw type changed to: {self.draw_type.get()}"
        log(msg)