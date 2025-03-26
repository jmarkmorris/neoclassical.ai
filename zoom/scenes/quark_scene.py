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
            # Create the main Quark using the base class method
            # This will automatically load the quark image
            quark_radius = 3
            quark = self.create_object(
                "Quark",
                [0, 0, 0],
                quark_radius
            )
            elements.append(quark)
            
            print(f"Created {len(elements)} Quark scene elements")
            return elements
        except Exception as e:
            print(f"Error in Quark.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images