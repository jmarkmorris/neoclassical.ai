from manim import *

class LineOpacity(Scene):
    def construct(self):
        # Disable anti-aliasing
        config.anti_alias = False
        
        # Set up the scene with indigo background
        self.camera.background_color = "#4B0082"  # Indigo background
        
        # Improved title with higher resolution
        title = Text("Line Opacity Visualization (Even % from 0% to 100%)", 
                     color=WHITE, 
                     font_size=36).to_edge(UP, buff=0.5)
        self.add(title)
        
        # Create three rows for different stroke widths
        stroke_widths = [1, 2, 3]
        
        # Calculate vertical positions for the three rows with more spacing
        row_positions = [-1.5, 0, 1.5]
        
        # Create labels for each row with improved resolution
        for i, width in enumerate(stroke_widths):
            label = Text(f"Width: {width}", 
                         color=WHITE, 
                         font_size=28)
            label.to_edge(LEFT, buff=0.5).shift(UP * row_positions[i])
            self.add(label)
        
        # For each row (stroke width)
        for row_idx, stroke_width in enumerate(stroke_widths):
            # Create 51 vertical lines with opacity from 0 to 1 (even percentages only)
            for i in range(0, 101, 2):  # 0, 2, 4, ..., 98, 100
                # Calculate opacity (0 to 1)
                opacity = i / 100
                
                # Calculate x position (distribute evenly across the screen)
                x_pos = -5 + (i/2) * 0.2
                
                # Create a vertical line with exact stroke_width
                line = Line(
                    start=[x_pos, row_positions[row_idx] + 0.5, 0],  # Top point
                    end=[x_pos, row_positions[row_idx] - 0.5, 0],    # Bottom point
                    stroke_width=stroke_width,
                    stroke_color=WHITE,
                    stroke_opacity=opacity
                )
                
                self.add(line)
        
        # Add opacity percentage markers with improved visibility
        for i in range(0, 101, 25):
            # Calculate x position to match the lines
            x_pos = -5 + (i/2) * 0.2
            
            # Create a tick using a line
            tick = Line(
                start=[x_pos, -3.0, 0],
                end=[x_pos, -3.3, 0],
                stroke_width=2,
                stroke_color=WHITE
            )
            
            # Add percentage label with improved visibility
            percentage = Text(f"{i}%", 
                              color=WHITE, 
                              font_size=24)
            percentage.next_to(tick, DOWN, buff=0.1)
            
            self.add(tick, percentage)

# To render the scene, run:
# manim -pql opacity_visualization.py OpacityVisualization