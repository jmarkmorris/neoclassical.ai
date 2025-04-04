from manim import *
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
import numpy as np
import random
from manim.utils.space_ops import angle_between_vectors
# Removed incorrect import: from manim.utils.color import Colors

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
    
    def animate_angle_change(self, target_angle_deg, run_time=2, rate_func=linear):
        """Returns an animation to change the angle to a target value."""
        # Calculate the rotation angle
        rotation_angle = (target_angle_deg - self.start_angle_deg) * DEGREES
        
        # Create the animation
        return Succession(
            Rotate(
                self.line2,
                angle=rotation_angle,
                about_point=self.center_dot.get_center(),
                rate_func=rate_func,
                run_time=run_time
            ),
            UpdateFromFunc(
                self.angle_arc,
                lambda m: m.become(self._update_angle_arc(target_angle_deg))
            ),
            UpdateFromFunc(
                self.theta_label,
                lambda m: self._update_theta_label(target_angle_deg)
            )
        )
    
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
            self.theta_label.move_to(
                center + np.array([
                    radius * np.cos(mid_angle),
                    radius * np.sin(mid_angle),
                    0
                ])
            )
            self.theta_label.set_opacity(1)
        else:
            # Hide label for parallel lines
            self.theta_label.set_opacity(0)
        
        # Update the stored angle
        self.start_angle_deg = new_angle_deg


class MovingAngle(Scene): # Renamed class to match filename
    def construct(self):
        self.camera.background_color = INDIGO

        # Add title
        title = Text("Moving Angle Grid", font="Helvetica Neue", weight="LIGHT", font_size=36)
        title.to_edge(UP, buff=0.5)
        self.add(title)

        # Grid parameters
        rows = 3
        cols = 4
        x_spacing = 3
        y_spacing = 2
        x_start = -((cols - 1) * x_spacing) / 2
        y_start = ((rows - 1) * y_spacing) / 2

        grid_cells = [] # Store individual cell groups
        animations = []

        for row in range(rows):
            for col in range(cols):
                # Calculate position relative to grid center (0,0)
                x = x_start + col * x_spacing
                y = y_start - row * y_spacing
                position = np.array([x, y, 0])

                # Randomize angles
                start_angle_deg = random.uniform(0, 360)
                end_angle_deg = random.uniform(0, 360)
                # Ensure end angle is different from start angle
                while abs(end_angle_deg - start_angle_deg) < 10:
                    end_angle_deg = random.uniform(0, 360)

                # Randomize colors
                line1_color = random.choice(MANIM_COLORS)
                line2_color = random.choice(MANIM_COLORS)
                while line2_color == line1_color: # Ensure different colors for lines
                    line2_color = random.choice(MANIM_COLORS)
                dot_color = random.choice(MANIM_COLORS)
                theta_color = random.choice(MANIM_COLORS)
                angle_arc_color = random.choice(MANIM_COLORS)

                # Randomize rate function (30% chance of reversing)
                if random.random() < 0.3:
                    rate_func = there_and_back
                else:
                    rate_func = linear # or smooth

                # Create a self-contained angle assembly
                angle_assembly = AngleAssembly(
                    start_angle_deg=start_angle_deg,
                    end_angle_deg=end_angle_deg,
                    line1_color=line1_color,
                    line2_color=line2_color,
                    dot_color=dot_color,
                    angle_arc_color=angle_arc_color,
                    theta_color=theta_color,
                    radius=1.0
                )
                
                # Move the angle assembly to its grid position
                angle_assembly.move_to(position)
                
                # Add to grid cells
                grid_cells.append(angle_assembly)
                
                # Create animation for this angle
                animations.append(
                    angle_assembly.animate_angle_change(
                        end_angle_deg,
                        run_time=random.uniform(3, 7),
                        rate_func=rate_func
                    )
                )

        # Add the final grid group to the scene
        final_grid_group = VGroup(*grid_cells)
        self.add(final_grid_group)

        # Play all animations simultaneously
        self.play(*animations)
        
        # Demonstrate that the angle assemblies can move while maintaining their structure
        # Create a path for one of the angle assemblies to follow
        if len(grid_cells) > 0:
            # Select the first angle assembly for demonstration
            moving_angle = grid_cells[0]
            
            # Create a path
            path = ParametricFunction(
                lambda t: np.array([
                    2 * np.sin(t * 2),  # x-coordinate
                    1.5 * np.cos(t * 3),  # y-coordinate
                    0                   # z-coordinate
                ]),
                t_range=[0, TAU],
                color=YELLOW_A,
                stroke_opacity=0.3     # Subtle path visualization
            )
            self.add(path)
            
            # Move the angle along the path
            self.play(
                MoveAlongPath(moving_angle, path),
                run_time=5,
                rate_func=linear
            )

        self.wait()


class AnglePathDemo(Scene):
    """Demonstrates how AngleAssembly can move along a path while maintaining its structure."""
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title
        title = Text("Moving Angle Demo", font="Helvetica Neue", weight="LIGHT", font_size=36)
        title.to_edge(UP, buff=0.5)
        self.add(title)
        
        # Create an angle assembly
        angle = AngleAssembly(
            start_angle_deg=45,
            line1_color=BLUE,
            line2_color=RED,
            dot_color=WHITE,
            angle_arc_color=YELLOW,
            theta_color=GREEN,
            radius=1.5
        )
        
        # Create a complex path
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
        self.add(path)
        
        # Add the angle to the scene
        self.add(angle)
        
        # Animate the angle changing while stationary
        self.play(
            angle.animate_angle_change(135, run_time=2, rate_func=smooth)
        )
        self.wait(0.5)
        
        # Move the angle along the path
        self.play(
            MoveAlongPath(angle, path),
            run_time=8,
            rate_func=linear
        )
        
        # Animate the angle changing again after movement
        self.play(
            angle.animate_angle_change(270, run_time=2, rate_func=there_and_back)
        )
        
        self.wait()
