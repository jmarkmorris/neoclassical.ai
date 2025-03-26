"""
Molecule scene implementation for NPQG Zoom Animation
Represents molecular structures at the 10^-8 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class MoleculeScene(ZoomableScene):
    """Scene representing molecular structures at 10^-8 m scale"""
    
    def __init__(self, config, scale_value=-8):
        """
        Initialize the molecule scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -8 (10^-8 m)
        """
        super().__init__(config, scale_value, "Molecule")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Molecule scene elements")
        elements = []
        
        try:
            # Create the main Molecule using the base class method
            # This will automatically load the molecule image
            molecule_radius = 3
            molecule = self.create_object(
                "Molecule",
                [0, 0, 0],
                molecule_radius
            )
            elements.append(molecule)
            
            print(f"Created {len(elements)} Molecule scene elements")
            return elements
        except Exception as e:
            print(f"Error in Molecule.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images