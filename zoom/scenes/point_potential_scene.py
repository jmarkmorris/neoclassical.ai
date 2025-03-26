"""
Point Potential scene implementation for NPQG Zoom Animation
Represents point potentials at the 10^-60 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class PointPotentialScene(ZoomableScene):
    """Scene representing point potentials at 10^-60 m scale"""
    
    def __init__(self, config, scale_value=-60):
        """
        Initialize the point potential scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -60 (10^-60 m)
        """
        super().__init__(config, scale_value, "Point Potential")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating PointPotential scene elements")
        elements = []
        
        try:
            # Create the main PointPotential using the base class method
            # This will automatically load the pointpotential image
            pointpotential_radius = 3
            pointpotential = self.create_object(
                "PointPotential",
                [0, 0, 0],
                pointpotential_radius
            )
            elements.append(pointpotential)
            
            print(f"Created {len(elements)} PointPotential scene elements")
            return elements
        except Exception as e:
            print(f"Error in PointPotential.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images