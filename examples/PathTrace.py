from manim import *
import random
import numpy as np
INDIGO = "#4B0082"

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
        
        # Set a fixed random seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create multiple dots with different colors and path tracers
        dot_configs = [
            {'color': PURE_BLUE, 'path_color': BLUE_C},
            {'color': PURE_BLUE, 'path_color': BLUE_C},
            {'color': PURE_BLUE, 'path_color': BLUE_C},
            {'color': PURE_RED, 'path_color': RED_C},
            {'color': PURE_RED, 'path_color': RED_C},
            {'color': PURE_RED, 'path_color': RED_C}
        ]

        dots = []
        trails = []

        for config in dot_configs:
            # Create dot and path with styling
            dot = Dot(color=config['color'], radius=0.075)  # Increased dot size by 50%
            
            # Start the dot lower to avoid overlap with titles
            dot.move_to([0, -1, 0])
            
            # Create a path that will show the trail
            trail = VMobject(stroke_width=2, stroke_color=config['path_color'], stroke_opacity=0.5)
            trail.start_new_path(dot.get_center()) # Initialize trail with a point
            
            def create_update_trail(dot, trail):
                def update_trail(trail):
                    # Add a new line segment to the trail at each dot position
                    trail.add_line_to(dot.get_center())
                return update_trail
            
            trail.add_updater(create_update_trail(dot, trail))
            
            dots.append(dot)
            trails.append(trail)

        # Create random paths for each dot
        custom_paths = []
        for _ in range(len(dots)):
            custom_path = VMobject()
            points = [[0, -1, 0]]  # Start lower to avoid title overlap
            
            for _ in range(128):  # More points for a longer, more interesting path
                while True:
                    angle = random.uniform(0, TAU)
                    new_point = points[-1] + np.array([np.cos(angle), np.sin(angle), 0])
                    
                    # Keep the path in the lower 2/3 of the screen to avoid title
                    if (abs(new_point[0]) <= 7 and 
                        new_point[1] <= 2.5 and  # Stay below this y-value to avoid title
                        new_point[1] >= -3.75):
                        points.append(new_point)
                        break
                        
            custom_path.set_points_smoothly(points)
            custom_paths.append(custom_path)
        
        # Add all Mobjects to the scene, ensuring dots are on top
        for dot, trail in zip(dots, trails):
            self.add(trail, dot)
        
        # Animate dots along their respective paths
        self.play(
            *[MoveAlongPath(dot, custom_path, rate_func=linear) for dot, custom_path in zip(dots, custom_paths)], 
            run_time=30  # Slow down the movement by 50%
        ) 
        
        # Add a final animation to show the completed paths
        self.play(
            *[Flash(dot, color=YELLOW, flash_radius=0.3) for dot in dots],
            run_time=0.5
        )
        self.wait(2)

