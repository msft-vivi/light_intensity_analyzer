from . import *

class Config():
    def __init__(self):
        # ImageFrame related config.
        self.image_frame_min_width = 800
        self.image_frame_min_height = 600
        self.image_taken_lbl_percent = 0.9

        # TK window related config.
        self.window_min_width = 500
        self.window_min_height = 600
        
        self.target_color = "red"

if __name__ == "__main__":
    config = Config()