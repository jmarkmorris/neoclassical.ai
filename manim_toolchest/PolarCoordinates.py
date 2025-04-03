from manim import *
from tools import INDIGO

class PolarCoordinates(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Polar Coordinates Visualization",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "PolarPlane(azimuth_units, azimuth_step, size) + Vector(polar_to_point(r, θ))",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.3)
        
        self.add(title, subtitle)

        polar_plane = PolarPlane(  
            azimuth_units="PI radians",
            azimuth_step=12,
            size=6,  
            azimuth_label_font_size=33.6,  
            radius_config={"font_size": 33.6, "stroke_color": WHITE},
            background_line_style={
                "stroke_color": WHITE,
                "stroke_width": 2,
                "stroke_opacity": 1
            }
        ).add_coordinates()  
        self.add(polar_plane)

        vector = Vector(polar_plane.polar_to_point(3, PI/4), stroke_width=2)
        self.add(vector)
