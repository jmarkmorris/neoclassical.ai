"""
Electron scene implementation for NPQG Zoom Animation
Represents electron scale at the 10^-15 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class ElectronScene(ZoomableScene):
    """Scene representing the electron at 10^-15 m scale"""
    
    def __init__(self, config, scale_value=-15):
        """
        Initialize the electron scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -15 (10^-15 m)
        """
        super().__init__(config, scale_value, "Electron")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Electron scene elements")
        elements = []
        
        try:
            # Create the main electron boundary using the base class method
            # This will automatically load custom images if available
            electron_radius = 3
            electron_boundary = self.create_object(
                "Electron",
                [0, 0, 0],
                electron_radius
            )
            elements.append(electron_boundary)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            # Check if we're using custom images and if an image was successfully loaded
            # The image is always the second element in the group if it exists
            has_custom_image = self.use_custom_images and len(electron_boundary) > 2
                    
            if not self.use_custom_images or not has_custom_image:
                # Create the electron core
                try:
                    electron_core = self._create_electron_core()
                    elements.append(electron_core)
                except Exception as e:
                    print(f"Error creating electron core: {e}")
                
                # Create the electron field
                try:
                    electron_field = self._create_electron_field()
                    elements.append(electron_field)
                except Exception as e:
                    print(f"Error creating electron field: {e}")
                
                # Create quantum fluctuations
                try:
                    quantum_fluctuations = self._create_quantum_fluctuations()
                    elements.append(quantum_fluctuations)
                except Exception as e:
                    print(f"Error creating quantum fluctuations: {e}")
                
                # Create electron-positron pairs
                try:
                    electron_positron_pairs = self._create_electron_positron_pairs()
                    elements.append(electron_positron_pairs)
                except Exception as e:
                    print(f"Error creating electron-positron pairs: {e}")
            
            print(f"Created {len(elements)} Electron scene elements")
            return elements
        except Exception as e:
            print(f"Error in Electron.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_electron_core(self):
        """Create the core of the electron"""
        electron_core = VGroup()
        
        # Central structure representing the electron "particle"
        core = Circle(
            radius=0.3,
            fill_color="#00FFFF",  # Cyan
            fill_opacity=0.9,
            stroke_color="#008B8B",  # Dark cyan
            stroke_width=2,
            stroke_opacity=1.0
        )
        
        # Add a pulsing effect with smaller concentric circles
        pulses = VGroup()
        num_pulses = 3
        for i in range(num_pulses):
            pulse = Circle(
                radius=0.3 + 0.1 * (i + 1),
                stroke_color="#00FFFF",
                stroke_width=2,
                stroke_opacity=0.7 - 0.2 * i,
                fill_opacity=0
            )
            pulses.add(pulse)
        
        # Inner quantum structure (represents quantum uncertainty)
        inner_structure = VGroup()
        num_particles = 20
        for _ in range(num_particles):
            # Random position within the core
            r = np.random.uniform(0, 0.25)
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Create a small dot
            dot = Dot(
                point=[x, y, 0],
                radius=0.02,
                color="#E0FFFF",  # Light cyan
                fill_opacity=np.random.uniform(0.5, 1.0)
            )
            
            inner_structure.add(dot)
        
        electron_core.add(core, pulses, inner_structure)
        return electron_core
    
    def _create_electron_field(self):
        """Create the electron's electromagnetic field"""
        field = VGroup()
        
        # Create field lines radiating outward
        num_lines = 24
        for i in range(num_lines):
            angle = i * TAU / num_lines
            
            # Starting point just outside the core
            start_radius = 0.4
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            # End point
            end_radius = 2.8  # Almost to the edge of the scene
            end_x = end_radius * np.cos(angle)
            end_y = end_radius * np.sin(angle)
            
            # Create the field line with decreasing opacity
            line = Line(
                start=[start_x, start_y, 0],
                end=[end_x, end_y, 0],
                stroke_color="#4169E1",  # Royal blue
                stroke_width=2,
                stroke_opacity=0.6
            )
            
            # Apply a gradient to the line
            line.set_opacity([0.8, 0.1])
            
            field.add(line)
        
        # Add circular field lines representing equipotential surfaces
        num_circles = 5
        for i in range(num_circles):
            radius = 0.6 + 0.4 * i
            
            circle = Circle(
                radius=radius,
                stroke_color="#4169E1",
                stroke_width=1,
                stroke_opacity=0.7 - 0.1 * i,
                fill_opacity=0
            )
            
            field.add(circle)
        
        return field
    
    def _create_quantum_fluctuations(self):
        """Create quantum vacuum fluctuations"""
        fluctuations = VGroup()
        
        # Number of fluctuation events
        num_fluctuations = 30
        
        for _ in range(num_fluctuations):
            # Random position within the scene
            r = np.random.uniform(0.5, 2.7)  # Away from core but within scene
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Create a small flashing dot for each fluctuation
            size = np.random.uniform(0.02, 0.08)
            opacity = np.random.uniform(0.3, 0.7)
            
            fluctuation = Circle(
                radius=size,
                fill_color="#BA55D3",  # Medium orchid (purplish)
                fill_opacity=opacity,
                stroke_width=0
            )
            fluctuation.move_to([x, y, 0])
            
            fluctuations.add(fluctuation)
        
        return fluctuations
    
    def _create_electron_positron_pairs(self):
        """Create virtual electron-positron pairs"""
        pairs = VGroup()
        
        # Number of pairs
        num_pairs = 8
        
        for i in range(num_pairs):
            # Random position and orientation
            r = np.random.uniform(1.0, 2.5)
            theta = np.random.uniform(0, TAU)
            
            center_x = r * np.cos(theta)
            center_y = r * np.sin(theta)
            
            # Random orientation angle
            orientation = np.random.uniform(0, TAU)
            
            # Distance between electron and positron
            separation = np.random.uniform(0.1, 0.3)
            
            # Calculate positions
            electron_x = center_x + separation/2 * np.cos(orientation)
            electron_y = center_y + separation/2 * np.sin(orientation)
            
            positron_x = center_x - separation/2 * np.cos(orientation)
            positron_y = center_y - separation/2 * np.sin(orientation)
            
            # Create the electron (cyan/blue)
            electron = Circle(
                radius=0.07,
                fill_color="#00FFFF",  # Cyan
                fill_opacity=0.8,
                stroke_color="#0000FF",  # Blue
                stroke_width=1,
                stroke_opacity=1.0
            )
            electron.move_to([electron_x, electron_y, 0])
            
            # Create the positron (magenta/red)
            positron = Circle(
                radius=0.07,
                fill_color="#FF00FF",  # Magenta
                fill_opacity=0.8,
                stroke_color="#FF0000",  # Red
                stroke_width=1,
                stroke_opacity=1.0
            )
            positron.move_to([positron_x, positron_y, 0])
            
            # Create a connecting line representing the pair creation
            connection = DashedLine(
                start=[electron_x, electron_y, 0],
                end=[positron_x, positron_y, 0],
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=0.5
            )
            
            # Create a small glow around the pair
            glow = Circle(
                radius=separation + 0.1,
                fill_color="#FFFFFF",
                fill_opacity=0.1,
                stroke_width=0
            )
            glow.move_to([center_x, center_y, 0])
            
            pair = VGroup(glow, connection, electron, positron)
            pairs.add(pair)
        
        return pairs