
## manim PointMovingOnShapes.py PointMovingOnShapes -pqh --disable_caching -p

from manim import *
from tools import INDIGO

class PointMovingOnShapes(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        
        circle = Circle(radius=1, color=WHITE)
        dot = Dot(color=PURE_BLUE).shift(RIGHT)

        self.play(GrowFromCenter(circle))
        self.add(dot)
        self.play(MoveAlongPath(dot, circle), run_time=2, rate_func=linear)
        self.wait()
