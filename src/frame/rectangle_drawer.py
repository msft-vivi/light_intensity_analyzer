from . import *

class RectangleDrawer(tk.Frame):
    def __init__(self, master, rectangle_values) -> None:
        super().__init__(master)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111, projection='3d')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.redraw(rectangle_values)
    
    def redraw(self, rectangle_values):
        # Generate the x, y coordinates of 3D graph.
        x, y = np.meshgrid(np.arange(rectangle_values.shape[1]), np.arange(rectangle_values.shape[0]))

        # Plot the surface.
        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        self.axes.set_zlabel("Light Intensity")
        self.axes.invert_xaxis()
        self.surf_img = self.axes.plot_surface(x, y, np.array(rectangle_values), cmap='viridis')

        # Generate the color bar.
        self.fig.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        self.ax_color_bar = plt.axes((0.85, 0.1, 0.02, 0.8))
        self.fig.colorbar(self.surf_img, cax=self.ax_color_bar, orientation='vertical')
        self.canvas.draw()
