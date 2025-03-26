"""
Image loading utility for NPQG Universe Zoom Animation
Handles loading and scaling images for use in scenes
"""

import os
from manim import *

class ImageLoader:
    """Utility for loading and scaling images for use in scenes"""
    
    def __init__(self, config):
        """
        Initialize the image loader
        
        Args:
            config (dict): Global configuration
        """
        self.config = config
        self.image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      "assets", "images")
        os.makedirs(self.image_dir, exist_ok=True)
        
        # Create subdirectories for different scales if they don't exist
        self.scale_dirs = [
            "universe", "galaxy_cluster", "galaxy", "black_hole", 
            "solar_system", "star", "molecule", "atom", 
            "electron", "quark", "point_potential"
        ]
        
        for dir_name in self.scale_dirs:
            os.makedirs(os.path.join(self.image_dir, dir_name), exist_ok=True)
    
    def get_image_for_scale(self, scale_name, image_index=0):
        """
        Get an image for a specific scale
        
        Args:
            scale_name (str): Name of the scale (e.g., "universe", "galaxy")
            image_index (int, optional): Index if multiple images are available
            
        Returns:
            ImageMobject or None: Loaded image or None if not found
        """
        print(f"Attempting to load image for scale: {scale_name}")
        
        # Normalize scale name (remove "Scene" suffix if present)
        orig_scale_name = scale_name
        if scale_name.endswith("Scene"):
            scale_name = scale_name[:-5].lower()
        else:
            scale_name = scale_name.lower()
        
        print(f"Normalized scale name: {scale_name}")
        
        # Find corresponding directory
        dir_path = None
        for dir_name in self.scale_dirs:
            if scale_name in dir_name or dir_name in scale_name:
                dir_path = os.path.join(self.image_dir, dir_name)
                print(f"Found matching directory: {dir_name}")
                break
        
        if not dir_path:
            print(f"No matching directory found for scale '{orig_scale_name}'")
            return None
            
        if not os.path.exists(dir_path):
            print(f"Image directory for scale '{scale_name}' not found at path: {dir_path}")
            return None
        
        print(f"Searching for images in: {dir_path}")
        
        # List image files in the directory
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            found_files = [f for f in os.listdir(dir_path) if f.lower().endswith(ext)]
            if found_files:
                print(f"Found {len(found_files)} files with extension {ext}: {found_files}")
                image_files.extend(found_files)
        
        if not image_files:
            print(f"No images found in {dir_path}")
            return None
        
        print(f"Total image files found: {len(image_files)}")
        
        # Get the requested image or default to the first one
        try:
            image_file = image_files[image_index % len(image_files)]
            print(f"Selected image: {image_file} (index {image_index})")
        except IndexError:
            if image_files:
                image_file = image_files[0]
                print(f"Using first image: {image_file}")
            else:
                print("No images available")
                return None
        
        # Load the image
        try:
            image_path = os.path.join(dir_path, image_file)
            print(f"Loading image from: {image_path}")
            image = ImageMobject(image_path)
            print(f"Successfully loaded image: {image_path}")
            return image
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def create_circular_image(self, image, circle_radius):
        """
        Create a circular image by masking a rectangular image
        
        Args:
            image (ImageMobject): The image to make circular
            circle_radius (float): Radius of the circle
            
        Returns:
            Group: A group containing the masked circular image
        """
        if image is None:
            return None
            
        # Create a reference circle for masking
        mask_circle = Circle(
            radius=circle_radius,
            fill_opacity=1,
            fill_color=WHITE,
            stroke_width=0
        )
        
        # Calculate scaling factor - scale image larger than needed
        # to ensure it fills the entire circle
        image_width = image.get_width()
        image_height = image.get_height()
        max_dimension = max(image_width, image_height)
        
        # Scale to slightly larger than circle diameter to avoid showing edges
        scale_factor = (circle_radius * 2.2) / max_dimension
        image.scale(scale_factor)
        
        # Center the image
        image.move_to(ORIGIN)
        
        # Return a custom ImageWithCircleMask object
        return self.create_masked_image(image, mask_circle, circle_radius)
    
    def create_masked_image(self, image, mask, radius):
        """
        Create a masked circular image using SVG clipping
        
        Args:
            image (ImageMobject): The image to mask
            mask (Circle): The circular mask
            radius (float): The radius of the circle
            
        Returns:
            Group: A group containing the properly masked circular image
        """
        # Create a circle that will form the visible boundary
        circle = Circle(
            radius=radius,
            stroke_width=0,
            fill_opacity=1,
            fill_color="#333333"  # Dark background
        )
        
        # We'll stack these elements:
        # 1. A background circle (dark color)
        # 2. The image positioned to fill the circle
        # 3. A circular outline for the edge
        
        outline = Circle(
            radius=radius,
            stroke_width=2,
            stroke_color=WHITE,
            fill_opacity=0
        )
        
        # This is our custom "masking" technique in Manim
        # We'll use the zIndex feature to ensure proper ordering
        image.set_z_index(10)  # Place image above background
        circle.set_z_index(9)  # Place background below image
        outline.set_z_index(11)  # Place outline on top
        
        # Create a group with all elements
        result = Group(circle, image, outline)
        
        return result
    
    def fit_image_to_circle(self, image, circle_radius):
        """
        Legacy method maintained for compatibility
        Now uses the new circular image masking technique
        
        Args:
            image (ImageMobject): The image to scale
            circle_radius (float): Radius of the circle to fit into
            
        Returns:
            Group: A group containing the masked circular image
        """
        return self.create_circular_image(image, circle_radius)
    
    def get_fitted_image(self, scale_name, circle_radius, image_index=0):
        """
        Load an image for a scale and fit it to a circle
        
        Args:
            scale_name (str): Name of the scale
            circle_radius (float): Radius of the circle to fit into
            image_index (int, optional): Index if multiple images are available
            
        Returns:
            ImageMobject or None: Fitted image or None if not found
        """
        image = self.get_image_for_scale(scale_name, image_index)
        if image:
            return self.fit_image_to_circle(image, circle_radius)
        return None