"""
Galaxy scene implementation for NPQG Zoom Animation
Represents a galaxy at the 10^21 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class GalaxyScene(ZoomableScene):
    """Scene representing a galaxy at 10^21 m scale"""
    
    def __init__(self, config, scale_value=21):
        """
        Initialize the galaxy scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 21 (10^21 m)
        """
        super().__init__(config, scale_value, "Galaxy")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Galaxy scene elements")
        elements = []
        
        try:
            # Create the main galaxy using the base class method
            # This will automatically load the galaxy image
            galaxy_radius = 3
            galaxy = self.create_object(
                "galaxy",
                [0, 0, 0],
                galaxy_radius
            )
            elements.append(galaxy)
            
            print(f"Created {len(elements)} Galaxy scene elements")
            return elements
        except Exception as e:
            print(f"Error in Galaxy.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images