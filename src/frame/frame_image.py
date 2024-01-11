
from . import *

class ImageFrame(tk.Frame):
    def __init__(self, master : tk.Tk, config : Config, result_frame : 'ResultFrame'):
        super().__init__(master, relief=tk.SUNKEN, borderwidth=2)

        # General setup.
        self.config = config
        self.original_image = None
        self.draw_type = tk.StringVar(self)
        self.draw_type.set("Line")  # default value
        self.result_frame = result_frame

        # Geometry setup.
        self.master = master
        self.grid(row=0, column=1, sticky="nsew")

        # Make grid (0, 0) scalable when ImageFrame is resized.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Sub widgets setup.
        self.image_label = tk.Label(master=self, background="blue")
        self.image_label.grid_remove()

        # self.image_canvas = tk.Canvas(master=self, width=300, height=300, bg='green')
        self.image_canvas = tk.Canvas(master=self, width=300, height=300)
        self.image_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        # self.image_canvas.grid_remove()

        # Event binding.
        self.image_canvas.bind("<Button-1>", self.on_mouse_press)
        self.image_canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # In-memory variables.
        self.backup_gray_scale = None

    def get_image_size(self) -> 'tuple[int, int]':
        width = int(self.config.image_taken_lbl_percent * self.config.image_frame_min_width)
        height = int(self.config.image_taken_lbl_percent * self.config.image_frame_min_height)
        return (width, height)

    def load_image(self):
        self.file_path = askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if not self.file_path:
            log("No file selected")
            return

        # Load image to PIL.Image object.
        self.original_image = Image.open(self.file_path)
        new_width, new_height = self.get_image_size()
        self.image = self.original_image.copy()
        self.image = self.image.resize((new_width, new_height), Image.Resampling.NEAREST)
        self.tk_photo_image = ImageTk.PhotoImage(self.image)
        self.image_canvas.create_image(0, 0, anchor="nw", image=self.tk_photo_image)

    def on_mouse_press(self, event: tk.Event):
        self.recover_picture()
        self.start_x = self.end_x = event.x
        self.start_y = self.end_y = event.y
        msg = f"Clicked at: ({event.x}, {event.y})"
        log(msg)

    def on_mouse_move(self, event: tk.Event):
        self.end_x = event.x
        self.end_y = event.y
        msg = f"Dragged to: ({event.x}, {event.y})"
        log(msg)

    def on_mouse_release(self, event: tk.Event):
        self.end_x = event.x
        self.end_y = event.y
        msg = f"Released at: ({event.x}, {event.y})"
        log(msg)
        self.draw_shape()
    
    def draw_shape(self):
        if self.draw_type.get() == "Line":
            self.draw_line()
            line_pixels = self.get_line_pixels()
            current_gray_scale = self.convert_pixels_to_grayscale(line_pixels)
            data = {
                "key" : "line",
                "value" : current_gray_scale
            }
            self.backup_gray_scale = data
            self.result_frame.on_draw_event(**data)
        elif self.draw_type.get() == "Rectangle":
            self.draw_rectangle()
            rectangle_pixels = self.get_rectangle_pixels()
            rectangle_gray_scale = self.get_rectanle_gray_scale(rectangle_pixels)
            data = {
                "key" : "rectangle",
                "value" : rectangle_gray_scale
            }
            log("rectangle_gray_scale: {}".format(rectangle_gray_scale))
            self.result_frame.on_draw_event(**data)
    
    def get_rectanle_gray_scale(self, rectangle_pixels : 'list[tuple[int, int, int]]') -> 'list[int]':
        if self.config.target_color == "r":
            return rectangle_pixels[:, :, 0]
        elif self.config.target_color == "g":
            return rectangle_pixels[:, :, 1]
        elif self.config.target_color == "b":
            return rectangle_pixels[:, :, 2]
        # return [int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]) for pixel in rectangle_pixels]
        
    def get_rectangle_pixels(self):
        crop_rectangle = (self.start_x, self.start_y, self.end_x, self.end_y)
        cropped_image = self.image.crop(crop_rectangle)
        pixels = np.array(cropped_image)
        return pixels

    def draw_line(self):
        if self.original_image is None:
            return
        self.image_canvas.create_line(self.start_x, self.start_y, self.end_x, self.end_y, fill="red", width=2)

    def draw_rectangle(self):
        self.image_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red", width=2)

    def get_line_pixels(self):
        line_pixels = list(bham.bresenham(self.start_x, self.start_y, self.end_x, self.end_y))
        pixel_values = [self.image.convert("RGB").getpixel(pixel) for pixel in line_pixels]
        return pixel_values


    def recover_picture(self):
        if self.original_image is None:
            return
        self.image = self.original_image.copy()
        new_width, new_height = self.get_image_size()
        self.image = self.image.resize((new_width, new_height), Image.Resampling.NEAREST)
        self.tk_photo_image = ImageTk.PhotoImage(self.image)
        self.image_canvas.create_image(0, 0, anchor="nw", image=self.tk_photo_image)

    def convert_pixels_to_grayscale(self, pixels : 'list[tuple[int, int, int]]') -> 'list[int]':
        if self.config.target_color == "r":
            return [pixel[0] for pixel in pixels]
        elif self.config.target_color == "g":
            return [pixel[1] for pixel in pixels]
        elif self.config.target_color == "b":
            return [pixel[2] for pixel in pixels]
        # return [int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]) for pixel in pixels]

    def normalize(self):
        if self.backup_gray_scale is None or self.backup_gray_scale["key"] != "line":
            log("Invalid gray scale data, expected line data.")
            return
        
        normalized = [pixel / 255 for pixel in self.backup_gray_scale["value"]]
        log("normalized: {}".format(normalized))
        normalized = [2 * pixel - 1 for pixel in normalized]
        data = {
            "key" : "line",
            "value" : normalized
        }
        self.result_frame.on_draw_event(**data)
    
    def unnormalize(self):
        if self.backup_gray_scale is None or self.backup_gray_scale["key"] != "line":
            return
        self.result_frame.on_draw_event(**self.backup_gray_scale)