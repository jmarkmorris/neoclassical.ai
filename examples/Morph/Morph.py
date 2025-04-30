from manim import *
from manim.mobject.text.text_mobject import Text
from manim.animation.transform import Transform, ReplacementTransform, FadeTransform
from manim.animation.composition import AnimationGroup
from manim.animation.creation import Write
INDIGO = "#4B0082"
class Morph(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = INDIGO

        # Title for the demonstration
        title = Text("Manim Morphing Techniques", font_size=36).to_edge(UP)
        self.add(title)

        # Create a vertical stack of examples
        examples_y_positions = [2, 0]

        # 1. Standard Transform
        transform_text1 = Text("Before Transform", color=WHITE)
        transform_text2 = Text("After Transform", color=YELLOW)
        transform_text1.move_to(examples_y_positions[0] * UP)
        transform_text2.move_to(examples_y_positions[0] * UP)
        transform_label = Text("Standard Transform", font_size=24, color=BLUE).next_to(transform_text1, DOWN)
        
        self.play(Write(transform_text1), Write(transform_label))
        self.wait(1)
        self.play(Transform(transform_text1, transform_text2))
        self.wait(1)

        # 2. Replacement Transform
        replace_text1 = Text("Original Text", color=GREEN)
        replace_text2 = Text("Replaced Text", color=RED)
        replace_text1.move_to(examples_y_positions[1] * UP)
        replace_text2.move_to(examples_y_positions[1] * UP)
        replace_label = Text("Replacement Transform", font_size=24, color=BLUE).next_to(replace_text1, DOWN)
        
        self.play(Write(replace_text1), Write(replace_label))
        self.wait(1)
        self.play(ReplacementTransform(replace_text1, replace_text2))
        self.wait(1)

        # 3. Fade Transform
        fade_text1 = Text("Fading Out", color=ORANGE)
        fade_text2 = Text("Fading In", color=ORANGE)
        fade_text1.move_to(2 * DOWN)
        fade_text2.move_to(2 * DOWN)
        fade_label = Text("Fade Transform", font_size=24, color=BLUE).next_to(fade_text1, DOWN)
        
        self.play(Write(fade_text1), Write(fade_label))
        self.wait(1)
        self.play(FadeTransform(fade_text1, fade_text2))
        self.wait(1)

        # Final wait
        self.wait(2)
