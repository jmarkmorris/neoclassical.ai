from manim import *
from tools import INDIGO

class VectorArrow(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Create coordinate plane
        numberplane = NumberPlane()
        
        # Create vector elements
        dot = Dot(ORIGIN)
        arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
        
        # Add labels
        origin_text = Text('(0, 0)').next_to(dot, DOWN)
        tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
        
        # Add all elements to scene
        self.add(numberplane, dot, arrow, origin_text, tip_text)
