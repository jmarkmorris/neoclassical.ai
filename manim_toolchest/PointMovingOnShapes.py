from manim import *
from tools import INDIGO

class PointMovingOnShapes(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
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
