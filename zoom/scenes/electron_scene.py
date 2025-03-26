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
            # Create the main electron using the base class method
            # This will automatically load the electron image
            electron_radius = 3
            electron = self.create_object(
                "electron",
                [0, 0, 0],
                electron_radius
            )
            elements.append(electron)
            
            print(f"Created {len(elements)} Electron scene elements")
            return elements
        except Exception as e:
            print(f"Error in Electron.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images