# For type declaration
from typing import Optional, Any
# Image processing
from PIL import Image, ImageTk, ImageDraw
import cv2
# GUI
import tkinter as tk
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Math
import numpy as np
import bresenham as bham
from scipy.signal import argrelextrema
# Local imports
from .config import Config
from .utils import log