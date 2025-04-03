from manim import *
import random
from tools import INDIGO

class PathTrace(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Path Tracing Animation",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "path.add_updater(update_path) + MoveAlongPath(dot, custom_path)",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create dot and path
        dot = Dot()
        path = VMobject()
        path.set_points_as_corners([dot.get_center(), dot.get_center()])
        
        # Define path updater
        def update_path(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([dot.get_center()])
            path.become(previous_path)
            
        path.add_updater(update_path)
        self.add(path, dot)

        # Create random path within screen bounds
        custom_path = VMobject()
        points = [ORIGIN]
        
        for _ in range(30):
            while True:
                angle = random.uniform(0, TAU)
                new_point = points[-1] + np.array([np.cos(angle), np.sin(angle), 0])
                if (abs(new_point[0]) <= config.frame_width / 2 and 
                    abs(new_point[1]) <= config.frame_height / 2):
                    points.append(new_point)
                    break
                    
        custom_path.set_points_smoothly(points)
        
        # Animate dot along path
        self.play(
            MoveAlongPath(dot, custom_path, rate_func=linear), 
            run_time=30
        ) 
        self.wait()

