## manim VectorArrow.py VectorArrow -pqh --disable_caching -p

# NumberPlane
# Arrow
# Dot

from manim import *
from tools import INDIGO

class VectorArrow(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        
        dot = Dot(ORIGIN)
        arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
        numberplane = NumberPlane()
        origin_text = Text('(0, 0)').next_to(dot, DOWN)
        tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
        self.add(numberplane, dot, arrow, origin_text, tip_text)
