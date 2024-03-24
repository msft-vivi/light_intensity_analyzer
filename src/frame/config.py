from . import *

class Config():
    def __init__(self):
        # TK window related config.
        self.window_min_width = 1800

        self.control_frame_width = 150

        self.image_frame_width = (self.window_min_width - self.control_frame_width) * 0.5
        self.image_frame_height = self.image_frame_width * 9 / 16

        self.window_min_height = int(self.image_frame_height * 1.6)
        
        self.target_color = "red"

        self.window_scale = 0.8

if __name__ == "__main__":
    config = Config()