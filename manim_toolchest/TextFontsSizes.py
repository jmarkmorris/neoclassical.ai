from manim import *
from tools import INDIGO

class TextFontsSizes(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Text Fonts and Sizes Demo",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Text(text, font='Helvetica Neue', font_size=size, weight=weight)",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.3)
        
        self.add(title, subtitle)
        
        # Text content and formatting options
        sample_text = "Neoclassical Physics and Quantum Gravity"
        font = "Helvetica Neue"
        sizes = [12, 16, 24, 32]
        weights = ["BOLD", "MEDIUM", "NORMAL", "LIGHT", "THIN"]
        
        text_groups = []
        
        # Create text objects with different sizes and weights
        for size in sizes:
            for weight in weights:
                # Create sample text with current size and weight
                text_obj = Text(
                    sample_text, 
                    font=font, 
                    font_size=size, 
                    weight=weight
                )
                
                # Create info label
                info_label = Text(
                    f"({size}, {weight})", 
                    font=font, 
                    font_size=size, 
                    weight=weight
                )
                
                # Group text and info
                line = VGroup(text_obj, info_label).arrange(RIGHT)
                text_groups.append(line)
        
        # Position text groups
        for i, group in enumerate(text_groups):
            if i == 0:
                # Position first group in upper left
                group.to_corner(UL)
                group.shift(LEFT*0.25 + UP*0.25)
            else:
                # Position subsequent groups below previous ones
                group.next_to(text_groups[i-1], DOWN*0.4)
                group.align_to(text_groups[i-1], LEFT)
            
            self.add(group)
