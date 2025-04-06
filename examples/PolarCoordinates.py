from manim import *
INDIGO = "#4B0082"

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
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)

        # Create a smaller polar plane (80% of original size)
        polar_plane = PolarPlane(  
            azimuth_units="PI radians",
            azimuth_step=12,
            size=4.8,  # Reduced from 6 to 4.8 (80%)
            azimuth_label_font_size=22,  # Further reduced font size for x-axis labels
            radius_config={"font_size": 28, "stroke_color": WHITE},
            background_line_style={
                "stroke_color": WHITE,
                "stroke_width": 1.8,  # Slightly reduced stroke width
                "stroke_opacity": 1
            }
        ).add_coordinates()
        
        # Center the plane and move it down
        polar_plane.move_to(ORIGIN + DOWN * 0.5)
        
        # Add the plane to the scene
        self.add(polar_plane)

        # Create a vector with adjusted size (also moved down with the plane)
        vector = Vector(
            polar_plane.polar_to_point(2.4, PI/4) - polar_plane.get_center(), 
            color=RED_E,  # Bright red color
            stroke_width=1.8
        )
        vector.shift(polar_plane.get_center())  # Move to match the plane's position
        self.add(vector)
