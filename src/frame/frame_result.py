
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
        self.normalized_gray_scale = None
        self.unnormalized_gray_scale = None
        self.is_normalized = False
        self.normalized_peak_scatter_points = None
        self.unnormalized_peak_scatter_points = None
        self.normalized_valley_scatter_points = None
        self.unnormalized_valley_scatter_points = None
        self.original_indices_maximum = None
        self.original_indices_minmum = None
    
    def reset_variables(self):
        self.is_normalized = False
        
    # Event handlers: when ImageFrame captures an event, it will call the corresponding event handler.
    def on_draw_event(self, **data : Any):
        if data is None:
            log("No data to draw")
            return
        
        self.reset_variables()

        # If the data type is a line, plot it.
        if data["key"] == "line":
            self.unnormalized_gray_scale = data["value"]
            self.original_indices_maximum , self.original_indices_minmum = self.get_extreme_value_index(np.array(self.unnormalized_gray_scale))
            self.indices_maximum = self.original_indices_maximum.copy()
            self.indices_minmum = self.original_indices_minmum.copy()
            self.normalized_peak_scatter_points, self.normalized_valley_scatter_points = self.get_intial_normalized_scatter_points(self.unnormalized_gray_scale)
            self.unnormalized_peak_scatter_points, self.unnormalized_valley_scatter_points = self.plot_line_gray_scale(self.unnormalized_gray_scale)
            self.btn_normalize.grid(row=0, column=0, sticky="nsew")
            self.btn_unormalize.grid(row=0, column=1, sticky="nsew")

        # If the data type is a rectangle, plot it.
        elif data["key"] == "rectangle":
            line_gray_scale = data["value"]
            self.plot_rectangle_gray_scale(line_gray_scale)

        else:
            log("Invalid data")
            return

    def plot_line_gray_scale(self, line_gray_scale):
        # Create axes to figure.
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.btn_frame.grid(row=1, column=0, sticky="nsew")

        # Plot and show the data.
        line_gray_scale = np.array(line_gray_scale)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Light Intensity")
        self.ax.plot(np.arange(0, len(line_gray_scale), 1), line_gray_scale)

        # Enable interactive scatter plot.
        self.peak_scatter = self.ax.scatter(self.indices_maximum, line_gray_scale[self.indices_maximum], color='red', picker=True)
        self.valley_scatter = self.ax.scatter(self.indices_minmum, line_gray_scale[self.indices_minmum], color='green', picker=True)

        # Connect the pick event to the on_pick method
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Show the figure.
        self.canvas.draw()

        # Get the scatter points coordinates.
        return self.peak_scatter.get_offsets(), self.valley_scatter.get_offsets()

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
    
    def get_intial_normalized_scatter_points(self, values):
        indices_maximum, indices_minmum = self.get_extreme_value_index(np.array(values))
        peak_scatter_points = np.array([[index, 1] for index in indices_maximum])
        valley_scatter_points = np.array([[index, -1] for index in indices_minmum])
        return peak_scatter_points, valley_scatter_points
    
    def normalize(self):
        if self.unnormalized_gray_scale is None:
            log("Invalid gray scale data, expected line data.")
            return

        values = np.array(self.unnormalized_gray_scale)
        indices_maximum, indices_minmum = self.get_extreme_value_index(values)

        max_value = values.max()
        min_value = values.min()
        values[indices_maximum] = max_value
        values[indices_minmum] = min_value

        self.normalized_gray_scale = 2 * (values - min_value) / (max_value - min_value) - 1
        self.is_normalized = True
        self.plot_line_gray_scale(self.normalized_gray_scale)
    
    def unnormalize(self):
        if self.unnormalized_gray_scale is None:
            log("Invalid gray scale data, expected line data.")
            return

        self.is_normalized = False
        self.plot_line_gray_scale(self.unnormalized_gray_scale)

    def get_extreme_value_index(self, data):
        indices_maximum = list(argrelextrema(data, np.greater, order=1)[0])
        indices_minmum = list(argrelextrema(data, np.less, order=1)[0])
        return indices_maximum, indices_minmum
    
    def on_pick(self, event):
        # Remove values in-place.
        def remove_elem_at_index(values, index_to_remove):
            return values.pop(index_to_remove)
        
        # If ind is not empty, it means that the user has clicked on one of the scatter points.
        if len(event.ind) > 0:
            if event.artist == self.peak_scatter:
                remove_elem_at_index(self.indices_maximum, event.ind[0])
                
            elif event.artist == self.valley_scatter:
                remove_elem_at_index(self.indices_minmum, event.ind[0])
            else:
                log("Invalid artist")
                return
        else:
            log("Invalid event.ind")

        # Trigger the pick event and the click event exclusively.
        self.pick_event_occurred = True

        if self.is_normalized:
            self.plot_line_gray_scale(self.normalized_gray_scale)
        else:
            self.plot_line_gray_scale(self.unnormalized_gray_scale)
        
    def on_click(self, event):
        if self.pick_event_occurred:
            self.pick_event_occurred = False
            return

        click_x, click_y = event.xdata, event.ydata
        peak_distances = None
        valley_distances = None

        if self.is_normalized:
            peak_distances = np.sqrt((self.normalized_peak_scatter_points[:, 0] - click_x)**2 + (self.normalized_peak_scatter_points[:, 1] - click_y)**2)
            valley_distances = np.sqrt((self.normalized_valley_scatter_points[:, 0] - click_x)**2 + (self.normalized_valley_scatter_points[:, 1] - click_y)**2)
            log ("peak_distances: {}, valley_distances: {}".format(peak_distances, valley_distances))
        else:
            peak_distances = np.sqrt((self.unnormalized_peak_scatter_points[:, 0] - click_x)**2 + (self.unnormalized_peak_scatter_points[:, 1] - click_y)**2)
            valley_distances = np.sqrt((self.unnormalized_valley_scatter_points[:, 0] - click_x)**2 + (self.unnormalized_valley_scatter_points[:, 1] - click_y)**2)
            log ("peak_distances: {}, valley_distances: {}".format(peak_distances, valley_distances))

        closest_peak_index = np.argmin(peak_distances)
        log("closest_peak_index: {}, distance: {}".format(closest_peak_index, peak_distances[closest_peak_index]))

        closest_valley_index = np.argmin(valley_distances)
        log ("closest_valley_index: {}, distance: {}".format(closest_valley_index, valley_distances[closest_valley_index]))

        log ("before add: indices_maximum: {}".format(self.indices_maximum))
        if peak_distances[closest_peak_index] < valley_distances[closest_valley_index]:
            self.indices_maximum.append(self.original_indices_maximum[closest_peak_index])
            log ("after add: indices_maximum: {}".format(self.indices_maximum))
        else:
            self.indices_minmum.append(self.original_indices_minmum[closest_valley_index])
            log ("after add: indices_minmum: {}".format(self.indices_minmum))

        if self.is_normalized:
            self.plot_line_gray_scale(self.normalized_gray_scale)
        else:
            self.plot_line_gray_scale(self.unnormalized_gray_scale)