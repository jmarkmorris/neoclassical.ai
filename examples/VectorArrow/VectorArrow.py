from manim import *
INDIGO = "#4B0082"

class VectorArrow(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Vector Arrow Visualization",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Arrow(ORIGIN, [2, 2, 0]) on NumberPlane() with Text labels",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create coordinate plane
        numberplane = NumberPlane()
        
        # Create vector elements
        dot = Dot(ORIGIN)
        arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
        
        # Add labels
        origin_text = Text('(0, 0)', font="Helvetica Neue", weight="LIGHT").next_to(dot, DOWN)
        tip_text = Text('(2, 2)', font="Helvetica Neue", weight="LIGHT").next_to(arrow.get_end(), RIGHT)
        
        # Add all elements to scene
        self.add(numberplane, dot, arrow, origin_text, tip_text)
