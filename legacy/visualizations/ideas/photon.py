# # manim photon.py photon -pqm --disable_caching -p

from manim import *
import random
# import json

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"

run_time = 3
# run_time = 60
frame_rate = 30
# frame_rate = 60
# paused = False # add pause feature?

# powerpoint png export size
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate

class photon(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
        self.camera.background_color = INDIGO