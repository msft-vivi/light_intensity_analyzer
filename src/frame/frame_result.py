from . import *
from .line_drawer import LineDrawer
from .rectangle_drawer import RectangleDrawer

class ResultFrame(tk.Frame):
    def __init__(self, master : tk.Tk):
        super().__init__(master, relief=tk.SUNKEN, borderwidth=2)
        self.master = master

        # Create a Figure and Axes object.
        # Notice: fig = Figure() will not show color bar.
        self.fig = plt.figure()

        # Make (row=0, column=0) expandable.
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)
    
    # Event handlers: when ImageFrame captures an event, it will call the corresponding event handler.
    def on_draw_event(self, **data : Any):
        if data is None:
            log("No data to draw")
            return
    
        # If the data type is a line, plot it.
        if data["key"] == "line":
            line_values = np.array(data["value"])
            line_coords = np.arange(0, len(line_values), 1)
            self.line_drawer = LineDrawer(self, line_coords, line_values)
            self.line_drawer.grid(row=0, column=0, sticky="nsew")
            
        # If the data type is a rectangle, plot it.
        elif data["key"] == "rectangle":
            line_gray_scale = data["value"]
            self.rectangle_drawer = RectangleDrawer(self, line_gray_scale)
            self.rectangle_drawer.grid(row=0, column=0, sticky="nsew")

        else:
            log("Invalid data")
            return