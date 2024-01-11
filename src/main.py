# Argparse
import argparse

from frame.frame_controller import ControlFrame
from frame.frame_image import ImageFrame
from frame.frame_result import ResultFrame
from frame.config import Config
from frame import utils
import tkinter as tk

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Color Analyzer")
    parser.add_argument("--color", type=str.lower, help="Color to analyze", default="r")
    args = parser.parse_args()

    config = Config()
    utils.parse_args_to_config(args, config)

    window = tk.Tk()
    window.title("Simple Color Analyzer")
    window.rowconfigure(0, minsize=config.window_min_height, weight=1)
    window.columnconfigure(1, minsize=config.window_min_width + 100, weight=1)
    window.columnconfigure(2, minsize=config.window_min_width, weight=1)
    result_frame = ResultFrame(master=window) 
    image_frame = ImageFrame(master=window, config=config, result_frame=result_frame)
    ControlFrame(master=window, image_frame=image_frame)
    window.mainloop()