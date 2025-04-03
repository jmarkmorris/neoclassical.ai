from manim import *
from tools import INDIGO

class MovingFrameBox(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Create product rule equation
        text = MathTex(
            "\\frac{d}{dx}f(x)g(x)=",
            "f(x)\\frac{d}{dx}g(x)",
            "+",
            "g(x)\\frac{d}{dx}f(x)"
        )
        
        # Create surrounding rectangles
        framebox1 = SurroundingRectangle(text[1], buff=0.1)
        framebox2 = SurroundingRectangle(text[3], buff=0.1)
        
        # Animate the equation and boxes
        self.play(Write(text))
        self.play(Create(framebox1))
        self.wait()
        self.play(ReplacementTransform(framebox1, framebox2))
        self.wait()
