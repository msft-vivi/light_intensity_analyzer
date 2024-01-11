
from . import *

class ResultFrame(tk.Frame):
    def __init__(self, master : tk.Tk):
        super().__init__(master, relief=tk.SUNKEN, borderwidth=2)
        self.master = master
        self.grid(row=0, column=2, sticky="nsew")

        # Create a Figure and Axes object.
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax_3d = self.fig.add_subplot(111, projection='3d')

        # Create a canvas to display the figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  

        # Get the widget from the canvas and pack it into the frame
        self.result_canvas_tk = self.canvas.get_tk_widget()
        # result_canvas_tk.grid(row=0, column=0, sticky="nsew")

    def on_draw_event(self, **data : Any):
        if data is None:
            log("No data to draw")
            return
        self.fig.clear()
        if data["key"] == "line":
            self.fig.add_axes(self.ax)
            line_gray_scale = data["value"]
            self.plot_line_gray_scale(line_gray_scale)
            pass
        elif data["key"] == "rectangle":
            self.fig.add_axes(self.ax_3d)
            line_gray_scale = data["value"]
            self.plot_rectangle_gray_scale(line_gray_scale)
            pass
        else:
            log("Invalid data")
            return

    def plot_line_gray_scale(self, line_gray_scale : 'list[int]'):
        x = np.arange(0.0, len(line_gray_scale), 1)
        y = np.array(line_gray_scale)

        # Clear the Axes.
        self.ax.clear()

        # Plot and show the data.
        self.ax.plot(x, y)
        self.canvas.draw()
        self.result_canvas_tk.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def plot_rectangle_gray_scale(self, rectangle_gray_scale : 'list[int]'):
        log("plot_rectangle_gray_scale")
        # Create a new figure and add a 3D subplot

        # Get the dimensions of the grayscale image
        height, width = rectangle_gray_scale.shape

        # Generate the x, y coordinates
        x = np.arange(width)
        y = np.arange(height)
        x, y = np.meshgrid(x, y)

        # Plot the surface
        self.ax_3d.plot_surface(x, y, rectangle_gray_scale, cmap='viridis')
        self.ax_3d.invert_xaxis()

        self.canvas.draw()
        self.result_canvas_tk.pack(side=tk.TOP, fill=tk.BOTH, expand=1)