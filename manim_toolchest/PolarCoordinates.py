from manim import *
from tools import INDIGO

class PolarCoordinates(Scene):
    def construct(self):
        self.camera.background_color = INDIGO

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
