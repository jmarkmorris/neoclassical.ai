## manim PathTrace.py PathTrace -pqh --disable_caching -p

from manim import *
import random
from tools import INDIGO

class PathTrace(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        
        path = VMobject()
        dot = Dot()
        path.set_points_as_corners([dot.get_center(), dot.get_center()])
        def update_path(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([dot.get_center()])
            path.become(previous_path)
        path.add_updater(update_path)
        self.add(path, dot)

        # define a custom meandering path for the dot to follow
        custom_path = VMobject()
        points = [ORIGIN]
        for i in range(30):
            while True:
                angle = random.uniform(0, TAU)
                new_point = points[-1] + np.array([np.cos(angle), np.sin(angle), 0])
                if abs(new_point[0]) <= config.frame_width / 2 and abs(new_point[1]) <= config.frame_height / 2:
                    points.append(new_point)
                    break
        custom_path.set_points_smoothly(points)
        self.play(MoveAlongPath(dot, custom_path, rate_func=linear), run_time=30) 
        self.wait()





