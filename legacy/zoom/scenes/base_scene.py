"""
Base scene implementation for NPQG Universe Zoom Animation
All specific scene types inherit from this base class
"""

import os
import sys
from manim import *
from manim.mobject.types.image_mobject import ImageMobject

# Add the project root to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.image_loader import ImageLoader

class ZoomableScene:
    """Base class for all zoomable scenes"""
    
    def __init__(self, config, scale_value, scene_name="Generic"):
        """
        Initialize a zoomable scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value (10^scale_value)
            scene_name (str): The name of the scene
        """
        self.config = config
        self.scale_value = scale_value
        self.scene_name = scene_name
        self.objects = []
        self.scale_indicator = None
        self.background = None
        self.parent_scene = None  # Will be set by ZoomManager
        
        # Initialize the image loader
        self.image_loader = ImageLoader(config)
        
        # Check if we should use custom images
        self.use_custom_images = config.get("global_settings", {}).get("use_custom_images", True)
        
    def setup(self):
        """Initialize scene components"""
        self.setup_background()
        self.setup_scale_indicator()
        
    def setup_background(self):
        """Create the background with the configured color"""
        # Extract settings from config
        bg_color = self.config["global_settings"].get("background_color", "#00FF00")  # Default to GREEN

        # Create a full-screen rectangle for the background
        self.background = Rectangle(
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0
        )
        # Center the background
        self.background.move_to(ORIGIN)
        # Don't call self.add here since this isn't a Manim Scene
        
    def setup_scale_indicator(self):
        """Create the 10^N scale indicator in top right corner"""
        # Format the scale text
        scale_text = f"10^{self.scale_value}"
        
        # Extract settings from config
        font_size = self.config["global_settings"].get("font_size", 24)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        
        # Create the scale indicator text
        self.scale_indicator = Text(
            scale_text,
            font="Arial",
            font_size=font_size,
            color=text_color
        )
        
        # Position in top right corner with padding
        self.scale_indicator.to_corner(UR, buff=0.5)
        # Don't call self.add here since this isn't a Manim Scene
        
    def create_object(self, label, position, radius, image_index=0):
        """
        Create a circle with an optional image at the specified position
        
        Args:
            label (str): The label text for the object (not displayed, just for reference)
            position (list): The [x, y, z] position coordinates
            radius (float): The radius of the circle
            image_index (int, optional): Index of the image to use if multiple are available
            
        Returns:
            Group: A group containing the circle and optionally a circular image
        """
        # Extract settings from config
        stroke_width = self.config["global_settings"].get("stroke_width", 2)
        circle_color = self.config["global_settings"].get("color_circle", "#FFFFFF")
        
        # Convert position list to 3D array if needed
        if isinstance(position, list):
            if len(position) == 2:
                position = [position[0], position[1], 0]
            position = np.array(position)
        
        # Create elements list
        elements = []
        has_image = False
        
        # Try to add a custom image if available and enabled
        if self.use_custom_images:
            # Only try to get an image if custom images are explicitly enabled
            image_result = self.image_loader.get_fitted_image(self.scene_name, radius, image_index)
            if image_result:
                has_image = True
                
                # The image_result is already a Group with proper masking
                # Just need to position it
                image_result.move_to(position)
                
                # Add the whole group to our elements
                elements.append(image_result)
        
        # If no image, create a solid color circle
        if not has_image:
            # Extract settings from config for the solid color circle
            fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
            fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
            
            # Create a plain circle with solid color fill (no label)
            circle = Circle(
                radius=radius,
                stroke_color=circle_color,
                stroke_width=stroke_width,
                fill_color=fill_color,
                fill_opacity=fill_opacity,
                z_index=1  # Ensure circle is above background
            )
            circle.move_to(position)
            elements.append(circle)
        
        # Always use Group as it can contain any Mobject type
        obj = Group(*elements)
        self.objects.append(obj)
        
        # Don't call self.add here since this isn't a Manim Scene
        return obj
        
    def update_scale_indicator(self, new_scale):
        """
        Update the scale indicator during transitions
        
        Args:
            new_scale (float): The new scale value to display
        """
        # Format the new scale text
        new_text = f"10^{new_scale:.1f}"
        
        # Extract settings from config
        font_size = self.config["global_settings"].get("font_size", 24)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        
        # Create new indicator text
        new_indicator = Text(
            new_text,
            font="Arial",
            font_size=font_size,
            color=text_color
        )
        new_indicator.to_corner(UR, buff=0.5)
        
        # Animate the transition
        self.play(Transform(self.scale_indicator, new_indicator))
    
    def clear_objects(self):
        """Remove all objects from the scene"""
        for obj in self.objects:
            self.remove(obj)
        self.objects = []
