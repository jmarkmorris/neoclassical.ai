"""
Black Hole scene implementation for NPQG Zoom Animation
Represents a supermassive black hole at the 10^12 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class BlackHoleScene(ZoomableScene):
    """Scene representing a supermassive black hole at 10^12 m scale"""
    
    def __init__(self, config, scale_value=12):
        """
        Initialize the black hole scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 12 (10^12 m)
        """
        super().__init__(config, scale_value, "Black Hole")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Black Hole scene elements")
        elements = []
        
        try:
            # Create the main black hole region using the base class method
            # This will automatically load the black hole image
            bh_radius = 3
            bh_region = self.create_object(
                "Black Hole",
                [0, 0, 0],
                bh_radius
            )
            elements.append(bh_region)
            
            print(f"Created {len(elements)} Black Hole scene elements")
            return elements
        except Exception as e:
            print(f"Error in BlackHole.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
# No custom object creation methods needed as we're only using images