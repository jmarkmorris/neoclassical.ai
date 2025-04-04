from manim import *
from tools import INDIGO, ELECTRIC_PURPLE

class CircleSizes(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        

        # Create coordinate grid
        grid = NumberPlane(
            x_range=[-7, 7],
            y_range=[-4, 4],
            axis_config={
                "stroke_color": WHITE,
                "stroke_width": 1,
                "include_ticks": False,
                "include_tip": False,
            },
            background_line_style={
                "stroke_color": ELECTRIC_PURPLE,
                "stroke_width": 1,
            }
        )
        self.add(grid)

        # Define circle colors
        colors = [PURE_BLUE, PURE_RED]
        
        # Create circles with increasing radius
        radius = 0.002
        for y in range(4, -4, -1):
            for x in range(-7, 7):
                # Create left circle (blue)
                left_circle = Circle(
                    radius=radius, 
                    color=colors[0]
                ).move_to([x + 0.25, y-0.25, 0])
                left_circle.set_fill(color=colors[0], opacity=1)
                
                # Create right circle (red)
                right_circle = Circle(
                    radius=radius, 
                    color=colors[1]
                ).move_to([x + 0.75, y-0.25, 0])
                right_circle.set_fill(color=colors[1], opacity=1)
                
                # Add circles to scene
                self.add(left_circle, right_circle)

                # Add radius label
                label = Text(
                    f"r = {radius:.3f}", 
                    color=WHITE, 
                    font_size=16, 
                    font="Helvetica Neue",
                    weight="LIGHT"
                ).move_to([x + 0.5, y-0.75, 0])
                self.add(label)

                # Increment radius for next pair
                radius += 0.002



