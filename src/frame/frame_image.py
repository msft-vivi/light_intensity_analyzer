
from . import *

class ImageFrame(tk.Frame):
    def __init__(self, master : tk.Tk, config : Config, result_frame : 'ResultFrame'):
        super().__init__(master, relief=tk.RAISED, pady=5, padx=5)

        # General setup.
        self.config = config
        self.original_image = None
        self.draw_type = tk.StringVar(self)
        self.draw_type.set("Line")  # default value
        self.result_frame = result_frame

        # Geometry setup.
        self.master = master

        # Make grid (0, 0) scalable when ImageFrame is resized.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Sub widgets setup.
        # self.image_canvas = tk.Canvas(master=self, width=300, height=300, bg='green')
        self.image_canvas = tk.Canvas(master=self)
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        # self.image_canvas.grid(row=0, column=0, sticky="nsew")
        # self.image_canvas.grid_remove()

        # Event binding.
        self.image_canvas.bind("<Button-1>", self.on_mouse_press)
        self.image_canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.bind("<Configure>", lambda event: self.recover_picture())

        # In-memory variables.
        self.backup_gray_scale = None

    def get_image_size(self) -> 'tuple[int, int]':
        return self.winfo_width(), self.winfo_height()

    def load_image(self):
        self.file_path = askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if not self.file_path:
            log("No file selected")
            return

        # Load image to PIL.Image object.
        self.original_image = Image.open(self.file_path)
        frame_width, frame_height = self.get_image_size()
        self.image = self.original_image.copy()
        self.image = self.image.resize((frame_width, frame_height), Image.Resampling.NEAREST)
        self.tk_photo_image = ImageTk.PhotoImage(self.image)
        self.image_canvas.create_image(0, 0, anchor="nw", image=self.tk_photo_image)

    def on_mouse_press(self, event: tk.Event):
        self.recover_picture()
        self.start_x = self.end_x = event.x
        self.start_y = self.end_y = event.y

    def on_mouse_move(self, event: tk.Event):
        self.end_x = event.x
        self.end_y = event.y

    def on_mouse_release(self, event: tk.Event):
        self.end_x = event.x
        self.end_y = event.y
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
        left_x, right_x = sorted([self.start_x, self.end_x])
        top_y, bottom_y = sorted([self.start_y, self.end_y])
        crop_rectangle = (left_x, top_y, right_x, bottom_y)
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