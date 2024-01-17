from . import *

class LineDrawer(tk.Frame):
    def __init__(self, master, line_coords, line_values) -> None:
        super().__init__(master, background="red")

        # Create a Figure and some axes object.
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(211)
        self.axex2 = self.fig.add_subplot(212)

        # Create a canvas object which eanble to put matplot graph on tkinter.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.rowconfigure([0,1], weight=1)
        self.columnconfigure([0], weight=1)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        # Bind the event handler to the canvas.
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Buttons for adding and deleting points.
        self.btn_extreme = tk.StringVar(self, value="none")
        self.btn_extreme_control_group = tk.Frame(self)
        self.btn_extreme_control_group.grid(row=1, column=0)

        for i in range(5):
            self.btn_extreme_control_group.columnconfigure(i, weight=1)

        button_style = {'background': 'lightblue', 'font': ('Helvetica', '10'), 'relief': 'raised', 'borderwidth': 3}

        self.btn_add_maximum = tk.Button(self.btn_extreme_control_group, text="Add Maximum", command= lambda : self.btn_extreme.set("add_maximum"), **button_style)
        self.btn_add_maximum.grid(row=1, column=0, sticky="ew")

        self.btn_add_minimum = tk.Button(self.btn_extreme_control_group, text="Add Minimum", command= lambda : self.btn_extreme.set("add_minimum"), **button_style)
        self.btn_add_minimum.grid(row=1, column=1, sticky="ew")
        
        self.btn_delete_maximum = tk.Button(self.btn_extreme_control_group, text="Delete Maximum", command= lambda: self.btn_extreme.set("delete_maximum"), **button_style)
        self.btn_delete_maximum.grid(row=1, column=2, sticky="ew")

        self.btn_delete_minimum = tk.Button(self.btn_extreme_control_group, text="Delete Minimum", command= lambda: self.btn_extreme.set("delete_minimum"), **button_style)
        self.btn_delete_minimum.grid(row=1, column=3, sticky="ew")

        self.normalize = tk.Button(self.btn_extreme_control_group, text="Normalize", command= lambda: self.normalize_line(), **button_style)
        self.normalize.grid(row=1, column=4, sticky="ew")

        # Instance related variables.
        self.minimum_indices = []
        self.maximum_indices = []
        self.line_values = line_values
        self.line_indicecs = line_coords
        self.maximum_indices = []
        self.minimum_indices = []
        self.normalized_values = []

        # Threshold for determining whether a point is close to the clicked point.
        self.x_diff_threshold = 0.01
        self.y_diff_threshold = 0.01

        # Initialize operation.
        self.initialize()
        self.redraw(self.line_values)


    def initialize(self):
        self.maximum_indices, self.minimum_indices = self.get_extreme_points(self.line_values)
        self.original_maximum_indices = self.maximum_indices.copy()
        self.original_minimum_indices = self.minimum_indices.copy()
        maximum_coord = [(self.line_indicecs[i], self.line_values[i]) for i in self.maximum_indices]
        minimum_coord = [(self.line_indicecs[i], self.line_values[i]) for i in self.minimum_indices]
        log("maximum coord: {}".format(maximum_coord))
        log("minimum coord: {}".format(minimum_coord))

    def reset_figure(self):
        # self.fig.clf()
        self.axes.clear()

    def draw_line(self, x, y, axes, isPickerable=True):
        axes.plot(x, y, label='linear', color='red', picker=isPickerable)
    
    def draw_scatter(self, x, y, axes, color='green'):
        axes.scatter(x, y, label='scatter', color=color)
    
    def redraw(self, line_values):
        self.reset_figure()
        self.draw_line(self.line_indicecs, line_values, self.axes)
        self.draw_scatter(self.line_indicecs[self.maximum_indices], line_values[self.maximum_indices], self.axes)
        self.draw_scatter(self.line_indicecs[self.minimum_indices], line_values[self.minimum_indices], self.axes, color='blue')
        self.update_figure()
    
    def update_figure(self):
        self.canvas.draw()
        
    def on_click(self, event):
        # Ensure the click event is in the axes (initial line graph) instead of normalized graph.
        if event.inaxes != self.axes:
            return

        click_x, click_y = event.xdata, event.ydata
        log(f'You clicked at coordinates ({click_x}, {click_y})')

        point_type = self.btn_extreme.get()
        log ("point_type: {}".format(point_type))

        if point_type == "delete_maximum":
            index_to_delete  =  self.get_closest_extreme_point_coord_x(click_x, click_y, "maximum")
            if index_to_delete == -1:
                return
            self.delete_point(index_to_delete, "maximum")
            self.redraw(self.line_values)

        elif point_type == "delete_minimum":
            index_to_delete =  self.get_closest_extreme_point_coord_x(click_x, click_y, "minimum")
            if index_to_delete == -1:
                return
            self.delete_point(index_to_delete, "minimum")
            self.redraw(self.line_values)

        elif point_type == "add_maximum":
            coord_x = self.get_closest_point_in_line(click_x, click_y)
            if coord_x == -1:
                return
            self.add_point(coord_x, "maximum")
            self.redraw(self.line_values)

        elif point_type == "add_minimum":
            coord_x = self.get_closest_point_in_line(click_x, click_y)
            if coord_x == -1:
                return
            self.add_point(coord_x, "minimum")
            self.redraw(self.line_values)
        else:
            log("Invalid point type")
    
    def delete_point(self, index_in_line, extreme_type):
        if extreme_type == "maximum":
            self.maximum_indices = [i for i in self.maximum_indices if i != self.line_indicecs[index_in_line]]
        elif extreme_type == "minimum":
            self.minimum_indices = [i for i in self.minimum_indices if i != self.line_indicecs[index_in_line]]           

    def add_point(self, index_in_line, point_type):
        if index_in_line in self.maximum_indices or index_in_line in self.minimum_indices:
            log("Point already in list")
            return

        if point_type == "maximum":
            self.maximum_indices = np.append(self.maximum_indices, index_in_line)
            self.maximum_indices = np.sort(self.maximum_indices)
        elif point_type == "minimum":
            self.minimum_indices = np.append(self.minimum_indices, index_in_line)
            self.minimum_indices = np.sort(self.minimum_indices)
        else:
            log("invalid point")

    def get_point_type(self, index_in_line):
        if index_in_line == 0:
            if self.line_values[index_in_line] > self.line_values[index_in_line + 1]:
                return "maximum"
            elif self.line_values[index_in_line] < self.line_values[index_in_line + 1]:
                return "minimum"
            else:
                log("invalid point")
        elif index_in_line == len(self.line_values) - 1:
            if self.line_values[index_in_line] > self.line_values[index_in_line - 1]:
                return "maximum"
            elif self.line_values[index_in_line] < self.line_values[index_in_line - 1]:
                return "minimum"
            else:
                log("invalid point")
        else:
            if self.line_values[index_in_line] > self.line_values[index_in_line - 1] and self.line_values[index_in_line] > self.line_values[index_in_line + 1]:
                return "maximum"
            elif self.line_values[index_in_line] < self.line_values[index_in_line - 1] and self.line_values[index_in_line] < self.line_values[index_in_line + 1]:
                return "minimum"
            else:
                log("invalid point")

    def get_closest_point_in_line(self, click_x, click_y):
        x_distances = np.abs(self.line_indicecs - click_x)
        x_closest_index = np.argmin(x_distances)
        y_distance_to_closest = np.abs(self.line_values[x_closest_index] - click_y)
        
        if self.is_nearest_point(x_distances[x_closest_index], len(self.line_indicecs), y_distance_to_closest, 255):
            return x_closest_index
        else:
            return -1

    def get_closest_extreme_point_coord_x(self, click_x, click_y, point_type):
        if point_type == "maximum":
            x_distances_to_all_maximum = np.abs(self.line_indicecs[self.maximum_indices] - click_x)
            x_closest_index_to_maximum = np.argmin(x_distances_to_all_maximum)
            coord_x_to_maximum = self.maximum_indices[x_closest_index_to_maximum]
            x_distances_to_closest_maximum = np.abs(coord_x_to_maximum - click_x)
            y_distance_to_closest_maximum = np.abs(self.line_values[coord_x_to_maximum] - click_y)

            if self.is_nearest_point(x_distances_to_closest_maximum, len(self.line_indicecs), y_distance_to_closest_maximum, 255):
                log(f'Closest point coord x is {self.line_indicecs[self.maximum_indices[x_closest_index_to_maximum]]}')
                return self.maximum_indices[x_closest_index_to_maximum]
            else:
                log("No close point found")
                return -1

        elif point_type == "minimum":
            x_distances_to_all_minimum = np.abs(self.line_indicecs[self.minimum_indices] - click_x)
            x_closest_index_to_minimum = np.argmin(x_distances_to_all_minimum)
            coord_x_to_minimum = self.minimum_indices[x_closest_index_to_minimum]
            x_distances_to_closest_minimum = np.abs(coord_x_to_minimum - click_x)
            y_distance_to_closest_minimum = np.abs(self.line_values[coord_x_to_minimum] - click_y)

            if self.is_nearest_point(x_distances_to_closest_minimum, len(self.line_indicecs), y_distance_to_closest_minimum, 255):
                log(f'Closest point coord x is {self.line_indicecs[self.minimum_indices[x_closest_index_to_minimum]]}')
                return self.minimum_indices[x_closest_index_to_minimum]
            else:
                log("No close point found")
                return -1
    
    def is_nearest_point(self, x, x_scale, y, y_scale):
        def normalize(x, x_scale):
            return x / x_scale
        dx = normalize(x, x_scale)
        dy = normalize(y, y_scale)
        log ("scaled distance to x, y is: ({}, {})".format(dx, dy))
        return dx < self.x_diff_threshold and dy < self.y_diff_threshold

    def get_extreme_points(self, y):
        maximum_indices = find_peaks(y)[0]
        minimum_indices = find_peaks(-y)[0]
        return maximum_indices, minimum_indices
    
    def normalize_line(self):
        max_value = np.max(self.line_values)
        min_value = np.min(self.line_values)

        self.normalized_values = []
        for i in range(len(self.line_values)):
            if i in self.maximum_indices:
                self.normalized_values.append(max_value)
            elif i in self.minimum_indices:
                self.normalized_values.append(min_value)
            else:
                self.normalized_values.append(self.line_values[i])
    
        log("len of normalized value: {}".format(len(self.line_values)))
        self.draw_normalized_graph(np.array(self.normalized_values))
    
    
    def draw_normalized_graph(self, normalized_values):
        self.axex2.clear()
        self.draw_line(self.line_indicecs, normalized_values, self.axex2, isPickerable=False)
        self.draw_scatter(self.line_indicecs[self.maximum_indices], normalized_values[self.maximum_indices], self.axex2)
        self.draw_scatter(self.line_indicecs[self.minimum_indices], normalized_values[self.minimum_indices], self.axex2, color='blue')
        self.update_figure()
    
    
    def get_input():
        value1 = self.input_entry1.get()
        print(value1)  # or do something else with the value

        value2 = self.input_entry2.get()
        print(value2)  # or do something else with the value