"""
Solar System scene implementation for NPQG Zoom Animation
Represents a solar system at the 10^11 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class SolarSystemScene(ZoomableScene):
    """Scene representing a solar system at 10^11 m scale"""
    
    def __init__(self, config, scale_value=11):
        """
        Initialize the solar system scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 11 (10^11 m)
        """
        super().__init__(config, scale_value, "Solar System")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating SolarSystem scene elements")
        elements = []
        
        try:
            # Create the main solar system using the base class method
            # This will automatically load the solarsystem image
            solar_system_radius = 3
            solar_system = self.create_object(
                "solar system",
                [0, 0, 0],
                solar_system_radius
            )
            elements.append(solar_system)
            
            print(f"Created {len(elements)} SolarSystem scene elements")
            return elements
        except Exception as e:
            print(f"Error in SolarSystem.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images