"""
Star scene implementation for NPQG Zoom Animation
Represents a star at the 10^9 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class StarScene(ZoomableScene):
    """Scene representing a star at 10^9 m scale"""
    
    def __init__(self, config, scale_value=9):
        """
        Initialize the star scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 9 (10^9 m)
        """
        super().__init__(config, scale_value, "Star")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Star scene elements")
        elements = []
        
        try:
            # Create the main star boundary using the base class method
            # This will automatically load the star image
            star_radius = 3
            star_boundary = self.create_object(
                "Star",
                [0, 0, 0],
                star_radius
            )
            elements.append(star_boundary)
            
            print(f"Created {len(elements)} Star scene elements")
            return elements
        except Exception as e:
            print(f"Error in Star.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
# No custom object creation methods needed as we're only using images