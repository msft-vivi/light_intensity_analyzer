from . import *
from .film_thickness import FilmThickness

class LineDrawer(tk.Frame):
    def __init__(self, master, line_coords, line_values) -> None:
        super().__init__(master)

        # Create a Figure and some axes object.
        self.fig = plt.figure()
        self.fig.subplots_adjust(hspace=0.8)
        self.axes = self.fig.add_subplot(411)
        self.axes2 = self.fig.add_subplot(412)
        self.axes3 = self.fig.add_subplot(413)
        self.axes4 = self.fig.add_subplot(414)

        # Create a canvas object which eanble to put matplot graph on tkinter.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.rowconfigure([0,1], weight=1)
        self.columnconfigure([0], weight=1)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        # Bind the event handler to the canvas.
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)

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
        self.normalize.grid(row=2, column=0, sticky="ew")

        self.btn_draw_thickness = tk.Button(self.btn_extreme_control_group, text="Draw Thickness", command= lambda: self.draw_thickness(), **button_style)
        self.btn_draw_thickness.grid(row=2, column=1, sticky="ew")

        # Initial point level.
        self.point_level = tk.StringVar(self)
        self.point_level.set("0")  # default value

        # self.point_level_label = tk.Label(self.btn_extreme_control_group, text="Initial Point Level:", font=("Helvetica", 10), fg='blue')
        self.point_level_label = tk.Label(self.btn_extreme_control_group, text="Initial Point Level:", **button_style)
        self.point_level_label.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        options = ["0", "1", "2", "3", "4", "5", "6", "7"]
        self.point_level_menu = tk.OptionMenu(self.btn_extreme_control_group, self.point_level, *options)
        self.point_level_menu.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Instance related variables.
        self.minimum_indices = []
        self.maximum_indices = []
        self.line_values = line_values[:, 0]
        self.line_indicecs = line_coords
        self.maximum_indices = []
        self.minimum_indices = []
        self.normalized_values = []
        self.green_light_values = line_values[:, 1]

        # Mouse picked point coord.
        self.selected_point_x = None
        self.selected_point_y = None

        # Input extreme value coord which cooresponds to the mouse selected point.
        self.input_extreme_ind_x_for_selected = None
        self.input_extreme_ind_y_for_selected = None
        self.all_extreme_points = None

        self.selected_interval_start_x = -1
        self.selected_interval_end_x = -1

        # Threshold for determining whether a point is close to the clicked point.
        self.x_diff_threshold = 0.01
        self.y_diff_threshold = 0.01

        # Initialize operation.
        self.initialize()
        self.merge_extreme_points()
        self.redraw(self.line_values)
        log("all extreme points: {}".format(self.all_extreme_points))

        # Thickness
        self.thickness_x = None
        self.thickness_y = None
        self.input_point_level = 0

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

    def draw_line(self, x, y, axes, title, isPickerable=True):
        axes.plot(x, y, label='linear', color='red', picker=isPickerable)
        axes.set_title(title)
    
    def draw_scatter(self, x, y, axes, color='green'):
        axes.scatter(x, y, label='scatter', color=color)

    def draw_thickness(self):
        
        def get_initial_x_thicknes_point():
            inital_x = -1
            for ind, val in enumerate(self.all_extreme_points):
                if self.all_extreme_points[ind] < self.selected_point_x and self.all_extreme_points[ind + 1] > self.selected_point_x:
                    inital_x = val
                    break
            return inital_x
        
        assert self.selected_point_x != None and self.selected_point_y != None, "Please select inital level point from normalized plot first."
        
        # Get all the light intensity values for the extreme points.
        point_and_normalized_light_pairs = [(self.line_indicecs[i], self.normalized_values[i]) for i in self.all_extreme_points]

        # Split the points into left and right side of the selected point.
        left_pairs = [x for x in point_and_normalized_light_pairs if x[0] < self.selected_point_x]
        right_pairs = [x for x in point_and_normalized_light_pairs if x[0] > self.selected_point_x]

        # Decide the selected extreme point interval that the selected point is in.
        self.selected_interval_start_x, self.selected_interval_end_x = self.get_interval_from_extreme_points()
        assert self.selected_interval_start_x != -1 and self.selected_interval_end_x != -1
        
        # Get the initial x value for the thickness point.
        initial_x = get_initial_x_thicknes_point()
        assert initial_x != -1, "Initial x is not found"

        # Get all the thickness x value.
        self.thickness_x = [x[0] for x in left_pairs]
        self.thickness_x += [initial_x]
        self.thickness_x += [x[0] for x in right_pairs]

        # Get the initial point level from the input.
        initial_level = self.point_level.get()
        assert initial_level is not None and initial_level != "", "Initial level is not set"
        initial_level = int(initial_level)

        # Get all the thickness y value.
        self.thickness_y = [FilmThickness.get_thickness(len(left_pairs) - i + initial_level, x[1]) for i, x in enumerate(left_pairs)]
        self.thickness_y += [FilmThickness.get_thickness(0, initial_level)] # Initial point value.
        self.thickness_y += [FilmThickness.get_thickness(i + 1 + initial_level, x[1]) for i, x in enumerate(right_pairs)]

        assert len(self.thickness_x) == len(self.thickness_y)
        assert self.thickness_x is not None and self.thickness_y is not None , "Thickness x and y are not set"

        # Draw the thickness graph.
        self.axes3.clear()
        self.draw_line(self.thickness_x, self.thickness_y, self.axes3, "Film Thickness")
        self.update_figure()
    
    def redraw(self, line_values):
        self.print_extreme_points()
        self.reset_figure()
        self.draw_line(self.line_indicecs, line_values, self.axes, "Red Light Intensity")
        self.draw_scatter(self.line_indicecs[self.maximum_indices], line_values[self.maximum_indices], self.axes)
        self.draw_scatter(self.line_indicecs[self.minimum_indices], line_values[self.minimum_indices], self.axes, color='blue')
        self.draw_line(self.line_indicecs, self.green_light_values, self.axes4, "Green Light Intensity")
        self.update_figure()
    
    def update_figure(self):
        self.canvas.draw()
       
    def on_pick(self, event):
        # if event.inaxes == self.axes2:
        #     ind = event.ind
        #     log("ind: {}".format(ind))
        line = event.artist
        if line.axes == self.axes2:
            ind = event.ind[0]
            log("selected point ({}, {})".format(ind, line.get_ydata()[ind]))
            self.selected_point_x, self.selected_point_y = line.get_xdata()[ind], line.get_ydata()[ind]

            self.draw_normalized_graph(np.array(self.normalized_values))

    def on_click(self, event):
        # Ensure the click event is in the axes (initial line graph) instead of normalized graph.
        if event.inaxes == self.axes:
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

            # Merge the maximum and minimum indices.
            self.merge_extreme_points()

        # elif event.inaxes == self.axes2:
        #     click_x, click_y = event.xdata, event.ydata
        #     log(f'You clicked at coordinates ({click_x}, {click_y})')
            # if index_to_delete == -1:
            #     return
            # self.delete_point(index_to_delete, "maximum")
            # self.redraw(self.line_values)
    
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

        def get_indices_diff_greater_than_threshold(indices, kept_indices):
            return [x for x in indices if x in kept_indices]

        initial_maximum_indices = find_peaks(y)[0]
        initial_minimum_indices = find_peaks(-y)[0]

        threashold = np.average(y) * 0.5

        extreme_indices = np.sort(np.concatenate((initial_maximum_indices, initial_minimum_indices)))
        diffs = np.diff(y[extreme_indices])
        filtered_extreme_indices = extreme_indices[:-1][np.abs(diffs) > threashold]

        maximum_indices = get_indices_diff_greater_than_threshold(initial_maximum_indices, filtered_extreme_indices)
        minimum_indices = get_indices_diff_greater_than_threshold(initial_minimum_indices, filtered_extreme_indices)
        
        return maximum_indices, minimum_indices
    

    def normalize_line(self):
        # Reset the selected point when re-normalize the line.
        self.selected_point_x = None
        self.selected_point_y = None
        self.selected_interval_end_x = -1
        self.selected_interval_start_x = -1

        max_value = np.max(self.line_values)
        min_value = np.min(self.line_values)
        self.normalized_values = 2 * ((self.line_values - min_value) / (max_value - min_value)) - 1
        self.draw_normalized_graph(self.normalized_values)
    

    def merge_extreme_points(self):
        self.all_extreme_points = np.sort(np.append(self.maximum_indices, self.minimum_indices))

    
    def draw_normalized_graph(self, normalized_values):
        self.axes2.clear()
        self.axes2.set_ylim(-1.1, 1.2)
        self.draw_line(self.line_indicecs, normalized_values, self.axes2, "Normalized Light Intensity", isPickerable=False)
        self.draw_scatter(self.line_indicecs[self.maximum_indices], normalized_values[self.maximum_indices], self.axes2)
        self.draw_scatter(self.line_indicecs[self.minimum_indices], normalized_values[self.minimum_indices], self.axes2, color='blue')
        if self.selected_point_x is not None and self.selected_point_y is not None:
            self.axes2.plot(self.selected_point_x, self.selected_point_y, marker='o', color='red')
        self.update_figure()
    
    
    def get_offset_to_selected_point(self, index):
        if self.input_extreme_ind_x_for_selected is None or self.input_extreme_ind_y_for_selected is None:
            log("Not set input extreme point coord, treat is as (0, 0)")
            return 0
        else:
            x = self.input_extreme_ind_x_for_selected + self.input_extreme_ind_y_for_selected
            return index - x
        
    def get_interval_from_extreme_points(self):
        for i in range(len(self.all_extreme_points) - 1):
            if self.all_extreme_points[i] <= self.selected_point_x and self.all_extreme_points[i + 1] > self.selected_point_x:
                return i, i + 1
        return -1, -1
    
    def print_extreme_points(self):
        log("maximum indices: {}".format(self.maximum_indices))
        log("minimum indices: {}".format(self.minimum_indices))