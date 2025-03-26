"""
Atom scene implementation for NPQG Zoom Animation
Represents atomic structures at the 10^-10 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class AtomScene(ZoomableScene):
    """Scene representing atomic structures at 10^-10 m scale"""
    
    def __init__(self, config, scale_value=-10):
        """
        Initialize the atom scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -10 (10^-10 m)
        """
        super().__init__(config, scale_value, "Atom")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Atom scene elements")
        elements = []
        
        try:
            # Create the main atom boundary using the base class method
            # This will automatically load the atom image
            atom_radius = 3
            atom_boundary = self.create_object(
                "Atom",
                [0, 0, 0],
                atom_radius
            )
            elements.append(atom_boundary)
            
            print(f"Created {len(elements)} Atom scene elements")
            return elements
        except Exception as e:
            print(f"Error in Atom.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
# No custom object creation methods needed as we're only using images