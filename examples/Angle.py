# Assuming the necessary imports are already done:
from manim import *
import numpy as np
import random
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"

# Define a small epsilon to avoid floating point issues near PI
ANGLE_EPSILON = 1e-6

# Manim standard colors list (replace dynamic generation with a static list)
MANIM_COLORS = [
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL, PINK, GOLD, MAROON,
    BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E,
    TEAL_A, TEAL_B, TEAL_C, TEAL_D, TEAL_E,
    GREEN_A, GREEN_B, GREEN_C, GREEN_D, GREEN_E,
    YELLOW_A, YELLOW_B, YELLOW_C, YELLOW_D, YELLOW_E,
    GOLD_A, GOLD_B, GOLD_C, GOLD_D, GOLD_E,
    RED_A, RED_B, RED_C, RED_D, RED_E,
    MAROON_A, MAROON_B, MAROON_C, MAROON_D, MAROON_E,
    PURPLE_A, PURPLE_B, PURPLE_C, PURPLE_D, PURPLE_E,
    PINK, LIGHT_PINK, PURE_BLUE, PURE_GREEN, PURE_RED, LIGHT_BROWN, DARK_BROWN,
    # Add more colors as needed, ensuring they are valid Manim constants
]

class AngleAssembly(VGroup):
    """A self-contained angle visualization that maintains its internal structure when moved."""
    def __init__(
        self, 
        start_angle_deg=0, 
        end_angle_deg=45, 
        line1_color=BLUE, 
        line2_color=RED,
        dot_color=WHITE,
        angle_arc_color=YELLOW,
        theta_color=GREEN,
        radius=1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Store parameters
        self.radius = radius
        self.start_angle_deg = start_angle_deg
        self.end_angle_deg = end_angle_deg
        self.line1_color = line1_color
        self.line2_color = line2_color
        self.dot_color = dot_color
        self.angle_arc_color = angle_arc_color
        self.theta_color = theta_color
        
        # Create the center point (origin for this VGroup)
        self.center_dot = Dot(ORIGIN, radius=0.08, color=self.dot_color).set_z_index(3)
        
        # Create the first line (fixed reference line)
        self.line1 = Line(ORIGIN, RIGHT * self.radius, color=self.line1_color).set_z_index(1)
        
        # Create the second line (will be rotated)
        self.line2 = Line(
            ORIGIN, 
            RIGHT * self.radius, 
            color=self.line2_color
        ).set_z_index(1)
        
        # Rotate the second line to the start angle
        self.line2.rotate(self.start_angle_deg * DEGREES, about_point=ORIGIN)
        
        # Create the angle arc
        self.angle_arc = self._create_angle_arc()
        
        # Create the theta label
        self.theta_label = MathTex(r"\theta", color=self.theta_color).scale(0.7)
        self._position_theta_label()
        
        # Add all elements to the VGroup
        self.add(self.line1, self.line2, self.angle_arc, self.theta_label, self.center_dot)
    
    def _create_angle_arc(self):
        """Creates the angle arc between the two lines."""
        angle_val = abs(self.start_angle_deg * DEGREES)
        
        # Check if angle is valid for visualization
        if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
            arc = Arc(
                radius=0.5,
                angle=angle_val,
                color=self.angle_arc_color,
                fill_opacity=0.2
            ).set_z_index(2)
            
            # Position the arc correctly
            if self.start_angle_deg > 0:
                arc.rotate(0, about_point=ORIGIN)
            else:
                # If angle is negative, adjust the arc's position
                arc.rotate(self.start_angle_deg * DEGREES, about_point=ORIGIN)
            
            return arc
        else:
            # Return an invisible arc for parallel lines
            return Arc(radius=0.5, angle=0, color=self.angle_arc_color, opacity=0)
    
    def _position_theta_label(self):
        """Positions the theta label at the middle of the angle arc."""
        angle_val = abs(self.start_angle_deg * DEGREES)
        
        if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
            # Calculate the midpoint angle
            mid_angle = self.start_angle_deg / 2 * DEGREES
            
            # Position at midpoint with slight offset from origin
            radius = 0.7  # Slightly larger than the arc radius
            self.theta_label.move_to(
                np.array([
                    radius * np.cos(mid_angle),
                    radius * np.sin(mid_angle),
                    0
                ])
            )
            self.theta_label.set_opacity(1)
        else:
            # Hide label for parallel lines
            self.theta_label.set_opacity(0)
    
    def update_angle(self, dt):
        """Updates the angle continuously."""
        # Define a rate of change for the angle
        rate_of_change = 60 * DEGREES  # Degrees per second
        
        # Update the angle based on the time delta
        self.start_angle_deg += rate_of_change * dt
        
        # Keep the angle within 0-360 degrees
        self.start_angle_deg %= 360
        
        # Calculate the rotation angle
        rotation_angle = rate_of_change * dt
        
        # Rotate the second line
        self.line2.rotate(
            rotation_angle,
            about_point=self.center_dot.get_center()
        )
        
        # Update the angle arc and theta label
        self.angle_arc.become(self._update_angle_arc(self.start_angle_deg))
        self._position_theta_label()
        self.theta_label.become(self._update_theta_label(self.start_angle_deg))
    
    def _update_angle_arc(self, new_angle_deg):
        """Updates the angle arc for a new angle."""
        angle_val = abs(new_angle_deg * DEGREES)
        
        if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
            arc = Arc(
                radius=0.5,
                angle=angle_val,
                color=self.angle_arc_color,
                fill_opacity=0.2
            ).set_z_index(2)
            
            # Position the arc correctly based on the center of the assembly
            center = self.center_dot.get_center()
            arc.shift(center)
            
            if new_angle_deg > 0:
                arc.rotate(0, about_point=center)
            else:
                arc.rotate(new_angle_deg * DEGREES, about_point=center)
            
            return arc
        else:
            # Return an invisible arc for parallel lines
            return Arc(radius=0.5, angle=0, color=self.angle_arc_color, opacity=0)
    
    def _update_theta_label(self, new_angle_deg):
        """Updates the theta label position for a new angle."""
        angle_val = abs(new_angle_deg * DEGREES)
        center = self.center_dot.get_center()
        
        if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
            # Calculate the midpoint angle
            mid_angle = new_angle_deg / 2 * DEGREES
            
            # Position at midpoint with slight offset from origin
            radius = 0.7  # Slightly larger than the arc radius
            theta_label = MathTex(r"\theta", color=self.theta_color).scale(0.7)
            theta_label.move_to(
                center + np.array([
                    radius * np.cos(mid_angle),
                    radius * np.sin(mid_angle),
                    0
                ])
            )
            theta_label.set_opacity(1)
            return theta_label
        else:
            # Hide label for parallel lines
            theta_label = MathTex(r"\theta", color=self.theta_color).scale(0.7)
            theta_label.set_opacity(0)
            return theta_label


class Angle(Scene):
    def construct(self):
        # Assuming INDIGO is defined (e.g., INDIGO = "#4B0082")
        try:
            self.camera.background_color = INDIGO
        except NameError:
            print("Warning: INDIGO color not defined, using default background.")
            pass # Use default background if INDIGO is missing

        # Create angle object and add it directly to the scene
        angle_assembly = AngleAssembly(start_angle_deg=45, end_angle_deg=135, radius=1.5)
        self.add(angle_assembly)  # Add directly without animation

        # Add updater to angle to update it every frame right from the start
        angle_assembly.add_updater(lambda mob, dt: mob.update_angle(dt))
        
        # Create a complex path for the angle to follow
        path = ParametricFunction(
            lambda t: np.array([
                3 * np.sin(t * 2),  # x-coordinate
                2 * np.cos(t * 3),  # y-coordinate
                0                   # z-coordinate
            ]),
            t_range=[0, TAU],
            color=YELLOW_A,
            stroke_opacity=0.3     # Subtle path visualization
        )
        #self.add(path)
        
        # Move the angle along the path continuously
        self.play(
            MoveAlongPath(angle_assembly, path),
            run_time=15,           # Longer runtime for smooth movement
            rate_func=linear       # Constant speed along the path
        )
        
        # Let it run in the final position for a moment
        self.wait(2)
        
        # Important: Remove updater at the end of the scene
        angle_assembly.remove_updater(angle_assembly.update_angle)
