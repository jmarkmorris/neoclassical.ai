"""
Universe scale scene implementation for NPQG Zoom Animation
Represents the observable universe at the 10^26 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class UniverseScene(ZoomableScene):
    """Scene representing the observable universe at 10^26 m scale"""
    
    def __init__(self, config, scale_value=26):
        """
        Initialize the universe scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 26 (10^26 m)
        """
        super().__init__(config, scale_value, "Universe")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Universe scene elements")
        elements = []
        
        try:
            # Create the observable universe object using the base class method
            # This will automatically load the universe image
            universe_radius = 3
            universe = self.create_object(
                "Observable Universe",
                [0, 0, 0], 
                universe_radius
            )
            elements.append(universe)
            
            print(f"Created {len(elements)} Universe scene elements")
            return elements
        except Exception as e:
            print(f"Error in Universe.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
# No custom object creation methods needed as we're only using images