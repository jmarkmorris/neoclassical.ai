from manim import *

# Configuration: Set the color you want to use (PURE_RED or PURE_BLUE)
# You can change this to switch between colors
DOT_COLOR = PURE_RED
# DOT_COLOR = PURE_BLUE

class Dot3DOptionsGrid(ThreeDScene):
    def construct(self):
        # Default values for all options
        default_options = {
            "radius": 0.1,  # Always use 0.1 radius
            "resolution": (8, 4),
            "sheen_factor": 0.25,
            "sheen_direction": OUT,
            "ambient_strength": 0.15,
            "specular_strength": 0.25,
            "shininess": 10,
            "shadow": False,
        }
        
        # Different values to test for each option
        options_names = [
            "Resolution",
            "Sheen Factor",
            "Sheen Direction",
            "Ambient Strength",
            "Specular Strength",
            "Shininess",
            "Shadow",
        ]
        
        options_values = {
            "Resolution": [(32, 16), (16, 8), (8, 4), (4, 2), (2, 1)],
            "Sheen Factor": [1.0, 0.5, 0.25, 0.1, 0.0],
            "Sheen Direction": [OUT, UP, DOWN, LEFT, RIGHT],
            "Ambient Strength": [0.8, 0.3, 0.15, 0.05, 0.0],
            "Specular Strength": [1.0, 0.5, 0.25, 0.1, 0.0],
            "Shininess": [50, 20, 10, 5, 1],
            "Shadow": [True, False, False, False, False],
        }

        # Set up the 3D scene with proper orientation (looking from above)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.camera.frame_center = ORIGIN
        self.camera.frame_width = 16  # Wider view
        # Use high resolution
        config.pixel_width = 1920
        config.pixel_height = 1080
        
        # Adjust starting position to the left of the screen
        x_offset = -6  # Start more to the left
        
        # For each option (column)
        for col_index, option_name in enumerate(options_names):
            # Add column label at the top
            option_title = Text(option_name, font_size=24)
            option_title.move_to([x_offset + col_index * 2, 3, 0])
            self.add(option_title)
            
            # For each value of this option (rows)
            for row_index in range(5):
                # Create a sphere with fixed radius but default settings otherwise
                dot = Sphere(
                    radius=0.1,  # Always use 0.1 radius
                    resolution=(default_options["resolution"][0], default_options["resolution"][1]),
                ).set_color(DOT_COLOR)
                
                # Apply all default properties
                dot.set_sheen_factor(default_options["sheen_factor"])
                dot.set_sheen_direction(default_options["sheen_direction"])
                dot.set_shininess(default_options["shininess"])
                
                # Override the option being explored in this column
                if option_name == "Resolution":
                    value = options_values[option_name][row_index]
                    # We need to recreate the sphere with the new resolution
                    dot = Sphere(
                        radius=0.1,  # Always use 0.1 radius
                        resolution=value,
                    ).set_color(DOT_COLOR)
                    dot.set_sheen_factor(default_options["sheen_factor"])
                    dot.set_sheen_direction(default_options["sheen_direction"])
                    dot.set_shininess(default_options["shininess"])
                elif option_name == "Sheen Factor":
                    value = options_values[option_name][row_index]
                    dot.set_sheen_factor(value)
                elif option_name == "Sheen Direction":
                    value = options_values[option_name][row_index]
                    dot.set_sheen_direction(value)
                elif option_name == "Ambient Strength":
                    # Not directly supported in Manim's Sphere, skip
                    value = options_values[option_name][row_index]
                elif option_name == "Specular Strength":
                    # Not directly supported in Manim's Sphere, skip
                    value = options_values[option_name][row_index]
                elif option_name == "Shininess":
                    value = options_values[option_name][row_index]
                    dot.set_shininess(value)
                elif option_name == "Shadow":
                    # Not directly supported in Manim's Sphere, skip
                    value = options_values[option_name][row_index]
                
                # Add a value label
                value_label = Text(f"{value}", font_size=16)
                
                # Position the dot at the correct grid position
                y_pos = 2 - row_index * 1.0  # Start at the top, more space between rows
                dot.move_to([x_offset + col_index * 2, y_pos, 0])
                
                # Position the label to the left of the dot
                value_label.next_to(dot, LEFT, buff=0.3)
                
                # Add objects to the scene
                self.add(dot)
                self.add(value_label)
        
        # Set up better lighting for 3D
        self.renderer.camera.light_source.move_to(3*IN+7*OUT+7*RIGHT)
        self.wait(5)