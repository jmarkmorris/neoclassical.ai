from manim import *
INDIGO = "#4B0082"

class TextFontsSizes(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Text Fonts and Sizes Demo",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).move_to(ORIGIN).shift(UP * 3.5) # Center and shift up to avoid overlap
        
        subtitle = Text(
            "Text(text, font='Helvetica Neue', font_size=size, weight=weight)",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1).move_to(ORIGIN).shift(UP * 3) # Center and shift up
        
        self.add(title, subtitle)
        
        # Text content and formatting options
        sample_text = "Neoclassical Physics and Quantum Gravity"
        font = "Helvetica Neue"
        sizes = [16, 24, 32]
        weights = ["BOLD", "MEDIUM", "NORMAL", "LIGHT", "THIN"]
        
        text_groups = []
        
        # Create text objects with different sizes and weights
        for size in sizes:
            for weight in weights:
                # Create and center sample text with current size and weight
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
                
                # Group, arrange, and center text and info
                line = VGroup(text_obj, info_label).arrange(RIGHT)
                line.move_to(ORIGIN) # Center each line
                text_groups.append(line)

        # Arrange text groups vertically with smaller buff
        text_group = VGroup(*text_groups).arrange(DOWN, buff=0.1)
        
        # Position the text group below the subtitle
        text_group.next_to(subtitle, DOWN, buff=0.5)

        # Calculate the shift needed to center horizontally
        shift_distance = ORIGIN - text_group.get_center()
        
        # Apply the shift
        text_group.shift(shift_distance)

        self.add(text_group)
