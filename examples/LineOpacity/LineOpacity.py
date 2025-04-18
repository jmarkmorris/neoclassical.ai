from manim import *
INDIGO = "#4B0082"

class LineOpacity(Scene):
    def construct(self):
        # Disable anti-aliasing for clearer lines
        config.anti_alias = False
        
        # Set background color
        self.camera.background_color = INDIGO
        
        # Add title
        title = Text(
            "Line Opacity Visualization (Even % from 0% to 100%)", 
            color=WHITE, 
            font_size=36,
            font="Helvetica Neue",
            weight="LIGHT"
        ).to_edge(UP, buff=0.5)
        
        # Add subtitle showing line creation syntax
        subtitle = Text(
            "Line(start=[x, y, z], end=[x, y, z], stroke_width=w, stroke_opacity=o)",
            color=YELLOW,
            font_size=20,
            font="Helvetica Neue",
            weight="LIGHT"
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Define stroke widths and row positions
        stroke_widths = [1, 2, 3]
        row_positions = [-1.5, 0, 1.5]
        
        # Create a group to hold all visualization elements
        visualization_group = VGroup()
        
        # Add row labels
        for i, width in enumerate(stroke_widths):
            label = Text(
                f"Width: {width}", 
                color=WHITE, 
                font_size=28,
                font="Helvetica Neue",
                weight="LIGHT"
            )
            label.shift(LEFT * 5 + UP * row_positions[i])
            visualization_group.add(label)
        
        # Create opacity lines for each row
        for row_idx, stroke_width in enumerate(stroke_widths):
            for i in range(0, 101, 2):  # 0, 2, 4, ..., 100
                opacity = i / 100
                x_pos = -4.0 + (i/2) * 0.2  # Moved 1.0 to the right total
                
                line = Line(
                    start=[x_pos, row_positions[row_idx] + 0.5, 0],
                    end=[x_pos, row_positions[row_idx] - 0.5, 0],
                    stroke_width=stroke_width,
                    stroke_color=WHITE,
                    stroke_opacity=opacity
                )
                
                visualization_group.add(line)
        
        # Add percentage markers
        for i in range(0, 101, 25):
            x_pos = -4.0 + (i/2) * 0.2  # Moved 1.0 to the right total
            
            # Add tick mark
            tick = Line(
                start=[x_pos, -2.5, 0],  # Moved up by 0.5
                end=[x_pos, -2.8, 0],    # Moved up by 0.5
                stroke_width=2,
                stroke_color=WHITE
            )
            
            # Add percentage label
            percentage = Text(
                f"{i}%", 
                color=WHITE, 
                font_size=24,
                font="Helvetica Neue",
                weight="LIGHT"
            )
            percentage.next_to(tick, DOWN, buff=0.1)
            
            visualization_group.add(tick, percentage)
        
        # Center the visualization group horizontally and move it down
        visualization_group.move_to(ORIGIN)  # Center at origin
        visualization_group.shift(DOWN * 1.0)  # Move down to avoid subtitle overlap
        
        # Add the visualization group to the scene
        self.add(visualization_group)
