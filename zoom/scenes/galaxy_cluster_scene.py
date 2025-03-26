"""
Galaxy Cluster scene implementation for NPQG Zoom Animation
Represents galaxy clusters at the 10^23 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class GalaxyClusterScene(ZoomableScene):
    """Scene representing galaxy clusters at 10^23 m scale"""
    
    def __init__(self, config, scale_value=23):
        """
        Initialize the galaxy cluster scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 23 (10^23 m)
        """
        super().__init__(config, scale_value, "Galaxy Cluster")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating GalaxyCluster scene elements")
        elements = []
        
        try:
            # Create the main GalaxyCluster using the base class method
            # This will automatically load the galaxycluster image
            galaxycluster_radius = 3
            galaxycluster = self.create_object(
                "GalaxyCluster",
                [0, 0, 0],
                galaxycluster_radius
            )
            elements.append(galaxycluster)
            
            print(f"Created {len(elements)} GalaxyCluster scene elements")
            return elements
        except Exception as e:
            print(f"Error in GalaxyCluster.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]

# No custom object creation methods needed as we're only using images