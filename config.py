import os
import sys

WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "World Conquest"
RESOURCE_DIR = getattr(
    sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))
)
BASE_DIR = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else RESOURCE_DIR
)
DATA_DIR = os.path.join(RESOURCE_DIR, "data")
SAVE_DIR = os.path.join(BASE_DIR, "saves")
DAY_SECONDS = 2.0

