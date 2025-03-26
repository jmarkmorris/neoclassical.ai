"""
Quark scene implementation for NPQG Zoom Animation
Represents quark structures at the 10^-18 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class QuarkScene(ZoomableScene):
    """Scene representing quark structures at 10^-18 m scale"""
    
    def __init__(self, config, scale_value=-18):
        """
        Initialize the quark scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -18 (10^-18 m)
        """
        super().__init__(config, scale_value, "Quark")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Quark scene elements")
        elements = []
        
        try:
            # Create the main quark boundary
            quark_radius = 3
            quark_circle = Circle(
                radius=quark_radius,
                stroke_color=WHITE,
                stroke_width=2,
                fill_opacity=0
            )
            quark_label = Text(
                "Quark",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=WHITE
            )
            quark_boundary = VGroup(quark_circle, quark_label)
            elements.append(quark_boundary)
            
            # Create a proton structure (made of quarks)
            try:
                proton = self._create_proton()
                elements.append(proton)
            except Exception as e:
                print(f"Error creating proton: {e}")
            
            # Create gluon field
            try:
                gluon_field = self._create_gluon_field()
                elements.append(gluon_field)
            except Exception as e:
                print(f"Error creating gluon field: {e}")
            
            # Create quark-antiquark pairs
            try:
                quark_antiquark_pairs = self._create_quark_antiquark_pairs()
                elements.append(quark_antiquark_pairs)
            except Exception as e:
                print(f"Error creating quark-antiquark pairs: {e}")
            
            # Create strong force visualization
            try:
                strong_force = self._create_strong_force()
                elements.append(strong_force)
            except Exception as e:
                print(f"Error creating strong force: {e}")
            
            print(f"Created {len(elements)} Quark scene elements")
            return elements
        except Exception as e:
            print(f"Error in Quark.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_proton(self):
        """Create a proton made of three quarks"""
        proton = VGroup()
        
        # Create a container for the proton
        proton_boundary = Circle(
            radius=1.2,
            stroke_color="#FFFFFF",
            stroke_width=1,
            stroke_opacity=0.5,
            fill_color="#FFFFFF",
            fill_opacity=0.05
        )
        
        # Create the three valence quarks (2 up quarks, 1 down quark)
        quarks = VGroup()
        
        # Positions for the three quarks in a triangular arrangement
        positions = [
            [0, 0.7, 0],    # Top
            [-0.6, -0.4, 0], # Bottom left
            [0.6, -0.4, 0]   # Bottom right
        ]
        
        # Colors for up and down quarks
        colors = ["#FF0000", "#FF0000", "#0000FF"]  # Red (up), Red (up), Blue (down)
        
        for i, (pos, color) in enumerate(zip(positions, colors)):
            # Create the quark
            quark = Circle(
                radius=0.3,
                fill_color=color,
                fill_opacity=0.8,
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=1.0
            )
            quark.move_to(pos)
            
            # Add label
            label = Text(
                "u" if color == "#FF0000" else "d",
                font_size=14,
                color="#FFFFFF"
            )
            label.move_to(pos)
            
            quarks.add(quark, label)
        
        # Add quantum chromodynamics color charge visualization
        # Color charges are represented as small dots inside the quarks
        color_charges = VGroup()
        
        for i, pos in enumerate(positions):
            # Determine color charge (red, green, blue)
            if i == 0:
                charge_color = "#FF0000"  # Red
            elif i == 1:
                charge_color = "#00FF00"  # Green
            else:
                charge_color = "#0000FF"  # Blue
            
            # Create a small dot for the color charge
            charge = Dot(
                point=pos,
                radius=0.08,
                color=charge_color,
                fill_opacity=0.9
            )
            
            color_charges.add(charge)
        
        proton.add(proton_boundary, quarks, color_charges)
        return proton
    
    def _create_gluon_field(self):
        """Create visualization of the gluon field"""
        gluon_field = VGroup()
        
        # Create a background field representing the gluon sea
        gluon_sea = Circle(
            radius=2.0,
            fill_color="#8A2BE2",  # BlueViolet
            fill_opacity=0.05,
            stroke_width=0
        )
        
        # Add gluon paths connecting the quarks
        # Positions for the three quarks (matching proton creation)
        positions = [
            [0, 0.7, 0],    # Top
            [-0.6, -0.4, 0], # Bottom left
            [0.6, -0.4, 0]   # Bottom right
        ]
        
        # Create curved paths between quarks representing gluons
        for i in range(3):
            # Start and end positions
            start_pos = positions[i]
            end_pos = positions[(i + 1) % 3]
            
            # Calculate control point (bend the path outward)
            mid_x = (start_pos[0] + end_pos[0]) / 2
            mid_y = (start_pos[1] + end_pos[1]) / 2
            
            # Normal direction to the line
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            norm_x = -dy
            norm_y = dx
            
            # Normalize and scale
            norm_length = np.sqrt(norm_x**2 + norm_y**2)
            if norm_length > 0:
                norm_x /= norm_length
                norm_y /= norm_length
            
            # Control point
            ctrl_x = mid_x + 0.4 * norm_x
            ctrl_y = mid_y + 0.4 * norm_y
            
            # Create the path
            gluon_path = QuadraticBezier(
                start=start_pos,
                control=[ctrl_x, ctrl_y, 0],
                end=end_pos,
                stroke_color="#FF00FF",  # Magenta
                stroke_width=4,
                stroke_opacity=0.7
            )
            
            gluon_field.add(gluon_path)
        
        # Add small "gluon particles" along the paths
        num_gluons = 15
        for _ in range(num_gluons):
            # Random position near a path
            # Choose a random pair of quarks
            i = np.random.randint(0, 3)
            start_pos = positions[i]
            end_pos = positions[(i + 1) % 3]
            
            # Parametric position along the line
            t = np.random.uniform(0.1, 0.9)
            
            # Linear interpolation
            x = start_pos[0] * (1 - t) + end_pos[0] * t
            y = start_pos[1] * (1 - t) + end_pos[1] * t
            
            # Add some curvature (matching the path)
            mid_x = (start_pos[0] + end_pos[0]) / 2
            mid_y = (start_pos[1] + end_pos[1]) / 2
            
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            norm_x = -dy
            norm_y = dx
            
            # Normalize and scale
            norm_length = np.sqrt(norm_x**2 + norm_y**2)
            if norm_length > 0:
                norm_x /= norm_length
                norm_y /= norm_length
            
            # Adjust position with curvature
            curve_factor = 4 * t * (1 - t)  # Peaks in the middle
            x += 0.4 * curve_factor * norm_x
            y += 0.4 * curve_factor * norm_y
            
            # Create the gluon
            gluon = Circle(
                radius=0.05,
                fill_color=random.choice(["#FF00FF", "#00FFFF", "#FFFF00"]),  # Random color
                fill_opacity=0.9,
                stroke_width=0
            )
            gluon.move_to([x, y, 0])
            
            gluon_field.add(gluon)
        
        gluon_field.add(gluon_sea)
        return gluon_field
    
    def _create_quark_antiquark_pairs(self):
        """Create virtual quark-antiquark pairs in the quantum vacuum"""
        pairs = VGroup()
        
        # Number of pairs
        num_pairs = 10
        
        for _ in range(num_pairs):
            # Random position away from the proton
            r = np.random.uniform(1.4, 2.8)
            theta = np.random.uniform(0, TAU)
            
            center_x = r * np.cos(theta)
            center_y = r * np.sin(theta)
            
            # Random quark type (up, down, strange)
            quark_type = np.random.choice(["u", "d", "s"])
            
            # Colors based on quark type
            if quark_type == "u":
                quark_color = "#FF0000"  # Red
            elif quark_type == "d":
                quark_color = "#0000FF"  # Blue
            else:
                quark_color = "#00FF00"  # Green
            
            # Separation between quark and antiquark
            separation = np.random.uniform(0.2, 0.4)
            angle = np.random.uniform(0, TAU)
            
            quark_x = center_x + separation/2 * np.cos(angle)
            quark_y = center_y + separation/2 * np.sin(angle)
            
            antiquark_x = center_x - separation/2 * np.cos(angle)
            antiquark_y = center_y - separation/2 * np.sin(angle)
            
            # Create the quark
            quark = Circle(
                radius=0.1,
                fill_color=quark_color,
                fill_opacity=0.8,
                stroke_width=1,
                stroke_color="#FFFFFF",
                stroke_opacity=0.8
            )
            quark.move_to([quark_x, quark_y, 0])
            
            # Create the antiquark (complementary color)
            antiquark_color = quark_color  # Same base color
            
            antiquark = Circle(
                radius=0.1,
                fill_color=antiquark_color,
                fill_opacity=0.8,
                stroke_width=1,
                stroke_color="#FFFFFF",
                stroke_opacity=0.8
            )
            antiquark.move_to([antiquark_x, antiquark_y, 0])
            
            # Add a bar symbol to the antiquark
            bar = Line(
                start=[antiquark_x - 0.08, antiquark_y + 0.08, 0],
                end=[antiquark_x + 0.08, antiquark_y + 0.08, 0],
                stroke_color="#FFFFFF",
                stroke_width=2,
                stroke_opacity=1.0
            )
            
            # Add labels for the quark and antiquark
            q_label = Text(
                quark_type,
                font_size=12,
                color="#FFFFFF"
            )
            q_label.move_to([quark_x, quark_y, 0])
            
            aq_label = Text(
                quark_type,
                font_size=12,
                color="#FFFFFF"
            )
            aq_label.move_to([antiquark_x, antiquark_y, 0])
            
            # Create a connecting line representing the pair
            connection = DashedLine(
                start=[quark_x, quark_y, 0],
                end=[antiquark_x, antiquark_y, 0],
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=0.4
            )
            
            pair = VGroup(connection, quark, antiquark, bar, q_label, aq_label)
            pairs.add(pair)
        
        return pairs
    
    def _create_strong_force(self):
        """Create visualization of the strong force"""
        strong_force = VGroup()
        
        # Create a field representing the strong force
        field = Circle(
            radius=2.5,
            fill_color="#FF6347",  # Tomato (reddish)
            fill_opacity=0.05,
            stroke_width=0
        )
        
        # Add field lines representing the strong force potential
        num_lines = 16
        for i in range(num_lines):
            angle = i * TAU / num_lines
            
            # Start near the center
            start_radius = 0.2
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            # End near the boundary
            end_radius = 2.4
            end_x = end_radius * np.cos(angle)
            end_y = end_radius * np.sin(angle)
            
            # Create the field line
            line = Line(
                start=[start_x, start_y, 0],
                end=[end_x, end_y, 0],
                stroke_color="#FF4500",  # OrangeRed
                stroke_width=1,
                stroke_opacity=0.3
            )
            
            # Apply a gradient to the line
            line.set_opacity([0.6, 0.1])
            
            strong_force.add(line)
        
        # Add visual representation of the strong force potential increasing with distance
        num_circles = 8
        for i in range(num_circles):
            radius = 0.3 + i * 0.3
            
            # Make the opacity higher as we go outward (to show strength increases)
            opacity = 0.05 + i * 0.02
            
            circle = Circle(
                radius=radius,
                stroke_color="#FF4500",
                stroke_width=1,
                stroke_opacity=0.3,
                fill_color="#FF4500",
                fill_opacity=opacity
            )
            
            strong_force.add(circle)
        
        # Add radial gradient to illustrate confinement
        confinement = Circle(
            radius=2.0,
            fill_opacity=0,
            stroke_width=10,
            stroke_color="#FF4500",
            stroke_opacity=0.2
        )
        
        strong_force.add(field, confinement)
        return strong_force