# Argparse
import argparse

from frame.frame_controller import ControlFrame
from frame.frame_image import ImageFrame
from frame.frame_result import ResultFrame
from frame.config import Config
from frame import utils
import tkinter as tk
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Color Analyzer")
    parser.add_argument("--color", type=str.lower, help="Color to analyze", default="r")
    args = parser.parse_args()

    config = Config()
    utils.parse_args_to_config(args, config)

    init_window_size = "{}x{}".format(config.window_min_width, config.window_min_height)
    window = tk.Tk()
    window.geometry(init_window_size)
    window.protocol("WM_DELETE_WINDOW", sys.exit)
    window.title("Simple Light Intensity Analyzer")
    window.rowconfigure(0, minsize=config.image_frame_height, weight=1)
    window.columnconfigure(0, minsize=config.control_frame_width)
    window.columnconfigure(1, minsize=config.image_frame_width, weight=1)
    window.columnconfigure(2, minsize=config.image_frame_width, weight=1)

    result_frame = ResultFrame(master=window) 
    result_frame.grid(row=0, column=2, sticky="nsew")

    image_frame = ImageFrame(master=window, config=config, result_frame=result_frame)
    image_frame.grid(row=0, column=1, sticky="nsew")

    control_frame = ControlFrame(master=window, image_frame=image_frame)
    control_frame.grid(row=0, column=0, sticky="ns")

    window.mainloop()