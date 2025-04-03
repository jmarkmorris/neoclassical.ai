from manim import *
from tools import INDIGO, ELECTRIC_PURPLE

class WriteStuff(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Write Animation Example",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Write(example_text) + Write(example_tex) with LaTeX formatting",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create text and equation
        example_text = Tex(
            "This is some text", 
            tex_to_color_map={"text": ELECTRIC_PURPLE},
            font="Helvetica Neue"
        )
        
        example_tex = MathTex(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        
        # Group and arrange elements
        group = VGroup(example_text, example_tex)
        group.arrange(DOWN)
        group.width = config["frame_width"] - 2 * LARGE_BUFF

        # Animate writing
        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


