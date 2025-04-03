## manim TextFontsSizes.py TextFontsSizes -pqh --disable_caching -p
## You can also specify the weight using a numeric value, where higher values correspond to thicker fonts. 
## For example, you can use `weight=700` to specify a bold font or `weight=300` to specify a light font.
## Not all fonts support all weight options, so experiment to find the right combination of font and weight. 

from manim import *
from tools import INDIGO

class TextFontsSizes(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        
        text = "Neoclassical Physics and Quantum Gravity"
        fonts = ["Helvetica Neue"]
        sizes = [12, 16, 24, 32]
        weights = ["BOLD", "MEDIUM", "NORMAL", "LIGHT", "THIN"]
        texts = []
        for size in sizes:
            for weight in weights:
                t = Text(text, font=fonts[0], font_size=size, weight=weight)
                info_text = Text(f"({size}, {weight})", font=fonts[0], font_size=size, weight=weight)
                line = VGroup(t, info_text).arrange(RIGHT)
                texts.append(line)
        for i, t in enumerate(texts):
            if (i==0):
                t.to_corner(UL)
                t.shift(LEFT*0.25 + UP*0.25)
            else:
                t.next_to(texts[i-1], DOWN*0.4)
                t.align_to(texts[i-1], LEFT)
            self.add(t)
