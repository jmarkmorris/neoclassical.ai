from manim import *
from tools import INDIGO

class PointMovingOnShapes(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Point Moving on Shapes",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "MoveAlongPath(dot, circle) with GrowFromCenter animation",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create circle and dot
        circle = Circle(radius=1, color=WHITE)
        dot = Dot(color=PURE_BLUE).shift(RIGHT)

        # Animate
        self.play(GrowFromCenter(circle))
        self.add(dot)
        self.play(
            MoveAlongPath(dot, circle), 
            run_time=2, 
            rate_func=linear
        )
        self.wait()
