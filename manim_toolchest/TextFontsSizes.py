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
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Text content and formatting options
        sample_text = "Neoclassical Physics and Quantum Gravity"
        font = "Helvetica Neue"
        sample_text = "Neoclassical Physics and Quantum Gravity"
        sizes = [16, 24, 32]
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
        
        # Position text groups to avoid overlap
        current_y = 3  # Start near the top
        x_offset = -5 # Left align
        for i, group in enumerate(text_groups):
            group.move_to([x_offset, current_y, 0])
            current_y -= group.height + 0.1  # Move down by text height + small buffer

            self.add(group)

        # Center the entire block of text
        text_group = VGroup(*self.mobjects)
        text_group.move_to(ORIGIN)
