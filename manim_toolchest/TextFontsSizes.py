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
            # Calculate the position as if the 12pt fonts were still there
            # This keeps all text at the same location in the frame
            row_index = i // 5  # 5 weights per size
            if row_index == 0:
                # First size (16pt) - position as if it were the second size
                group.to_corner(UL)
                group.shift(LEFT*0.25 + UP*0.25 - DOWN*0.4*5)  # Move up by 5 rows (the number of weights)
            else:
                # For other sizes, position relative to the previous group
                group.next_to(text_groups[i-5], DOWN*0.4)  # -5 because we have 5 weights per size
                group.align_to(text_groups[i-5], LEFT)
            
            self.add(group)
