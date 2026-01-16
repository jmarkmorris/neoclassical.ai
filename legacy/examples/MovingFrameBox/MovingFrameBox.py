from manim import *
INDIGO = "#4B0082"

class MovingFrameBox(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Moving Frame Box Animation",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "SurroundingRectangle(text[1]) + ReplacementTransform(framebox1, framebox2)",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
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
