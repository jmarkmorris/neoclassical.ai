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
        
        # Create dot and path with styling
        dot = Dot(color=WHITE, radius=0.1)
        
        # Start the dot lower to avoid overlap with titles
        dot.move_to([0, -1, 0])
        
        # Create a path that will show the trail
        path = VMobject(stroke_width=2, stroke_color=YELLOW, stroke_opacity=0.8)
        trail = VMobject(stroke_width=2, stroke_color=WHITE, stroke_opacity=0.8)
        trail.set_points_as_corners([dot.get_center()]) # Initialize trail with a point

        path.set_points_as_corners([dot.get_center(), dot.get_center()])
        
        # Define path updater with fading trail effect
        def update_path(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([dot.get_center()])
            trail.add_smooth_curve_to(dot.get_center())
            
            # Limit the length of the trail
            if len(previous_path.get_points()) > 300:  # Keep a reasonable trail length
                # Remove the oldest points
                points = previous_path.get_points()[3:]
                previous_path.set_points(points)
            
            path.become(previous_path)
            
            # Create a gradient effect - fade out older parts of the trail
            n_points = len(path.get_points())
            if n_points > 0:
                colors = [
                    interpolate_color(BLACK, YELLOW, i/(n_points-1))
                    for i in range(n_points)
                ]
                path.set_rgba_array_direct(
                    np.array([color_to_rgba(c) for c in colors])
                )
        
        path.add_updater(update_path)
        self.add(path, dot, trail)

        # Create random path within screen bounds, staying in lower part of screen
        custom_path = VMobject()
        points = [[0, -1, 0]]  # Start lower to avoid title overlap
        
        for _ in range(40):  # More points for a longer, more interesting path
            while True:
                angle = random.uniform(0, TAU)
                new_point = points[-1] + np.array([np.cos(angle), np.sin(angle), 0])
                
                # Keep the path in the lower 2/3 of the screen to avoid title
                if (abs(new_point[0]) <= config.frame_width / 2 - 0.5 and 
                    new_point[1] <= 0.5 and  # Stay below this y-value to avoid title
                    new_point[1] >= -config.frame_height / 2 + 0.5):
                    points.append(new_point)
                    break
                    
        custom_path.set_points_smoothly(points)
        
        # Animate dot along path at a reasonable speed
        self.play(
            MoveAlongPath(dot, custom_path, rate_func=linear), 
            run_time=15  # Reduced from 30 to make it more engaging
        ) 
        
        # Add a final animation to show the completed path
        self.play(
            Flash(dot, color=YELLOW, flash_radius=0.3),
            run_time=0.5
        )
        self.wait(2)

