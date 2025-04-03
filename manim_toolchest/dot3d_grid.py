from manim import *
from tools import INDIGO

DOT_COLOR = PURE_RED

class Dot3DOptionsGrid(ThreeDScene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Default values for all options
        default_options = {
            "radius": 0.1,
            "resolution": (8, 4),
            "sheen_factor": 0.25,
            "sheen_direction": OUT,
            "ambient_strength": 0.15,
            "specular_strength": 0.25,
            "shininess": 10,
            "shadow": False,
        }
        
        # Options to display
        options_names = [
            "Resolution",
            "Sheen Factor",
            "Sheen Direction",
            "Ambient Strength",
            "Specular Strength",
            "Shininess",
            "Shadow",
        ]
        
        # Values for each option
        options_values = {
            "Resolution": [(32, 16), (16, 8), (8, 4), (4, 2), (2, 1)],
            "Sheen Factor": [1.0, 0.5, 0.25, 0.1, 0.0],
            "Sheen Direction": [OUT, UP, DOWN, LEFT, RIGHT],
            "Ambient Strength": [0.8, 0.3, 0.15, 0.05, 0.0],
            "Specular Strength": [1.0, 0.5, 0.25, 0.1, 0.0],
            "Shininess": [50, 20, 10, 5, 1],
            "Shadow": [True, False, False, False, False],
        }

        # Set up camera
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.camera.frame_center = ORIGIN
        self.camera.frame_width = 16
        
        # Set high resolution
        config.pixel_width = 1920
        config.pixel_height = 1080
        
        # Starting position
        x_offset = -6
        
        # Create grid of options
        for col_index, option_name in enumerate(options_names):
            # Add column header
            option_title = Text(option_name, font_size=24)
            option_title.move_to([x_offset + col_index * 2, 3, 0])
            self.add(option_title)
            
            # Add rows for each value
            for row_index in range(5):
                # Create default sphere
                dot = Sphere(
                    radius=0.1,
                    resolution=default_options["resolution"],
                ).set_color(DOT_COLOR)
                
                # Apply default properties
                dot.set_sheen_factor(default_options["sheen_factor"])
                dot.set_sheen_direction(default_options["sheen_direction"])
                dot.set_shininess(default_options["shininess"])
                
                # Apply specific option value
                value = options_values[option_name][row_index]
                
                if option_name == "Resolution":
                    # Recreate sphere with new resolution
                    dot = Sphere(
                        radius=0.1,
                        resolution=value,
                    ).set_color(DOT_COLOR)
                    dot.set_sheen_factor(default_options["sheen_factor"])
                    dot.set_sheen_direction(default_options["sheen_direction"])
                    dot.set_shininess(default_options["shininess"])
                elif option_name == "Sheen Factor":
                    dot.set_sheen_factor(value)
                elif option_name == "Sheen Direction":
                    dot.set_sheen_direction(value)
                elif option_name == "Shininess":
                    dot.set_shininess(value)
                
                # Create value label
                value_label = Text(f"{value}", font_size=16)
                
                # Position elements
                y_pos = 2 - row_index * 1.0
                dot.move_to([x_offset + col_index * 2, y_pos, 0])
                value_label.next_to(dot, LEFT, buff=0.3)
                
                # Add to scene
                self.add(dot, value_label)
        
        # Set lighting
        self.renderer.camera.light_source.move_to(3*IN+7*OUT+7*RIGHT)
        self.wait(5)
