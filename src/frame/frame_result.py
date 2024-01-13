
from . import *

class ResultFrame(tk.Frame):
    def __init__(self, master : tk.Tk):
        super().__init__(master, relief=tk.SUNKEN, borderwidth=2, background='red')
        self.master = master

        # Create a Figure and Axes object.
        # Notice: fig = Figure() will not show color bar.
        self.fig = plt.figure()

        # Create a canvas to display the figure.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  

        # Get the widget from the canvas and pack it into the frame
        self.result_canvas_tk = self.canvas.get_tk_widget()
        self.result_canvas_tk.grid(row=0, column=0, sticky="nsew")

        # Make (row=0, column=0) expandable.
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # Create a frame to contain the buttons to control the normalization.
        self.btn_frame = tk.Frame(master=self, relief=tk.SUNKEN, borderwidth=2)
        self.btn_frame.grid(row=1, column=0, sticky="nsew")
        self.btn_normalize = tk.Button(master=self.btn_frame, text="Normalize", command=self.normalize)
        self.btn_unormalize = tk.Button(master=self.btn_frame, text="Unormalize", command=self.unnormalize)
        self.btn_normalize.grid_remove()
        self.btn_unormalize.grid_remove()

        # In-memory variables.
        self.backup_gray_scale = None
    
    # Event handlers: when ImageFrame captures an event, it will call the corresponding event handler.
    def on_draw_event(self, **data : Any):
        if data is None:
            log("No data to draw")
            return

        # If the data type is a line, plot it.
        if data["key"] == "line":
            self.backup_gray_scale = data
            self.plot_line_gray_scale(self.backup_gray_scale["value"])
            self.btn_normalize.grid(row=0, column=0, sticky="nsew")
            self.btn_unormalize.grid(row=0, column=1, sticky="nsew")

        # If the data type is a rectangle, plot it.
        elif data["key"] == "rectangle":
            line_gray_scale = data["value"]
            self.plot_rectangle_gray_scale(line_gray_scale)

        else:
            log("Invalid data")
            return

    def plot_line_gray_scale(self, line_gray_scale : 'list[int]'):
        # Get the peak and valley value list.
        line_coordinates = np.arange(0, len(line_gray_scale), 1)
        line_values = np.array(line_gray_scale)
        indices_maximum = argrelextrema(line_values, np.greater, order=1)[0]
        indices_minmum = argrelextrema(line_values, np.less, order=1)[0]
        peak_value_coordinates = line_coordinates[indices_maximum]
        peak_values = line_values[indices_maximum]
        valley_value_coordinates = line_coordinates[indices_minmum]
        valley_values = line_values[indices_minmum]

        # Create axes to figure.
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.btn_frame.grid(row=1, column=0, sticky="nsew")

        # Plot and show the data.
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Light Intensity")
        self.ax.plot(line_coordinates, line_values)
        self.ax.scatter(peak_value_coordinates, peak_values, color='red')
        self.ax.scatter(valley_value_coordinates, valley_values, color='green')
        self.canvas.draw()

    def plot_rectangle_gray_scale(self, rectangle_gray_scale : 'list[(int, int)]'):
        # 3D plot does not need the button frame.
        self.btn_frame.grid_remove()

        # Create a new figure and add a 3D subplot.
        self.fig.clear()
        self.ax_3d = self.fig.add_subplot(111, projection='3d')

        # Generate the x, y coordinates.
        x, y = np.meshgrid(np.arange(rectangle_gray_scale.shape[1]), np.arange(rectangle_gray_scale.shape[0]))

        # Plot the surface.
        self.ax_3d.set_xlabel("X")
        self.ax_3d.set_ylabel("Y")
        self.ax_3d.set_zlabel("Light Intensity")
        self.ax_3d.invert_xaxis()
        self.surf_img = self.ax_3d.plot_surface(x, y, np.array(rectangle_gray_scale), cmap='viridis')

        # Generate the color bar.
        self.fig.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        self.ax_color_bar = plt.axes((0.85, 0.1, 0.02, 0.8))
        self.fig.colorbar(self.surf_img, cax=self.ax_color_bar, orientation='vertical')
        self.canvas.draw()
    
    def normalize(self):
        if self.backup_gray_scale is None or self.backup_gray_scale["key"] != "line":
            log("Invalid gray scale data, expected line data.")
            return

        grayscale_data = np.array(self.backup_gray_scale["value"])
        indices_maximum = argrelextrema(grayscale_data, np.greater, order=1)[0]
        indices_minmum = argrelextrema(grayscale_data, np.less, order=1)[0]
        max_value = np.max(grayscale_data)
        min_value = np.min(grayscale_data)
        grayscale_data[indices_maximum] = max_value
        grayscale_data[indices_minmum] = min_value


        normalized_data = 2 * (grayscale_data - min_value) / (max_value - min_value) - 1
        
        data = {
            "key" : "line",
            "value" : normalized_data
        }
        self.redraw(**data)
    
    def unnormalize(self):
        if self.backup_gray_scale is None or self.backup_gray_scale["key"] != "line":
            return
        self.redraw(**self.backup_gray_scale)

    def redraw(self, **data : Any):
        if data is None:
            log("No data to draw")
            return

        # Clear the figure.
        self.fig.clear()

        if data["key"] == "line":
            self.fig.add_axes(self.ax)
            self.plot_line_gray_scale(data["value"])
        elif data["key"] == "rectangle":
            self.fig.add_axes(self.ax_3d)
            line_gray_scale = data["value"]
            self.plot_rectangle_gray_scale(line_gray_scale)
        else:
            log("Invalid data")
            return