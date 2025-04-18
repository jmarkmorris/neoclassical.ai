"""
Image loading utility for Universe Zoom Animation
Implements a completely new approach to circular image masking and scaling
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from manim import *

class ImageLoader:
    """Utility for loading and creating properly masked circular images"""
    
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
        
        # Create directories if they don't exist
        for dir_name in self.scale_dirs:
            os.makedirs(os.path.join(self.image_dir, dir_name), exist_ok=True)
            
        # Keep a cache of processed images to avoid redundant processing
        self._processed_image_cache = {}
        
        # Track temp files for cleanup on destruction
        self._temp_files = []
        
        # Create a temporary directory for processed images
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "temp", "processed_images")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_image_for_scale(self, scale_name, image_index=0):
        """
        Get an image for a specific scale
        
        Args:
            scale_name (str): Name of the scale (e.g., "universe", "galaxy")
            image_index (int, optional): Index if multiple images are available
            
        Returns:
            str or None: Path to the image file or None if not found
        """
        # Normalize scale name (remove "Scene" suffix if present)
        orig_scale_name = scale_name
        if scale_name.endswith("Scene"):
            scale_name = scale_name[:-5].lower()
        else:
            scale_name = scale_name.lower()
        
        # Find corresponding directory
        dir_path = None
        for dir_name in self.scale_dirs:
            if scale_name in dir_name or dir_name in scale_name:
                dir_path = os.path.join(self.image_dir, dir_name)
                break
        
        if not dir_path or not os.path.exists(dir_path):
            return None
        
        # List image files in the directory
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg']:
            found_files = [f for f in os.listdir(dir_path) if f.lower().endswith(ext)]
            image_files.extend(found_files)
        
        if not image_files:
            return None
        
        # Get the requested image or default to the first one
        try:
            image_file = image_files[image_index % len(image_files)]
        except IndexError:
            if image_files:
                image_file = image_files[0]
            else:
                return None
        
        # Return the full path to the image
        image_path = os.path.join(dir_path, image_file)
        return image_path
    
    def create_circular_masked_image(self, image_path, radius):
        """
        Create a circular image using PIL for preprocessing and Manim ImageMobject for display
        
        Args:
            image_path (str): Path to the source image
            radius (float): Radius of the circle in Manim units
            
        Returns:
            Mobject: A mobject containing the properly masked circular image
        """
        if not image_path or not os.path.exists(image_path):
            return self._create_fallback_circle(radius)
        
        # Check if we already processed this image at this radius
        cache_key = f"{image_path}_{radius}"
        if cache_key in self._processed_image_cache:
            return self._processed_image_cache[cache_key]
        
        try:
            # Generate a unique filename for the processed image
            basename = os.path.basename(image_path)
            name, ext = os.path.splitext(basename)
            processed_path = os.path.join(self.temp_dir, f"{name}_circular{ext}")
            
            # Track the file for cleanup
            self._temp_files.append(processed_path)
            
            # Open the source image with PIL
            img = Image.open(image_path).convert("RGBA")
            
            # Create a circular mask
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            
            # Calculate the maximum inscribed circle
            width, height = img.size
            diameter = min(width, height)
            center_x, center_y = width // 2, height // 2
            
            # Draw a white circle on the mask
            draw.ellipse((center_x - diameter // 2, 
                         center_y - diameter // 2,
                         center_x + diameter // 2, 
                         center_y + diameter // 2), 
                         fill=255)
            
            # Apply the mask
            img_masked = Image.new("RGBA", img.size, (0, 0, 0, 0))
            img_masked.paste(img, (0, 0), mask)
            
            # Save the processed image
            img_masked.save(processed_path)
            
            # Load the processed image with Manim
            image_mobject = ImageMobject(processed_path)
            
            # Scale the image to match the desired radius
            current_width = image_mobject.get_width()
            scale_factor = (radius * 2) / current_width
            image_mobject.scale(scale_factor)
            
            # Create a circular outline
            stroke_color = self.config["global_settings"].get("color_circle", "#FFFFFF")
            stroke_width = self.config["global_settings"].get("stroke_width", 2)
            
            outline = Circle(
                radius=radius,
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                fill_opacity=0
            )
            
            # Group the image and outline
            result = Group(image_mobject, outline)
            
            # Cache the result
            self._processed_image_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return self._create_fallback_circle(radius)
    
    def _create_fallback_circle(self, radius):
        """Create a simple circle as a fallback when image processing fails"""
        # Extract settings from config for the solid color circle
        stroke_color = self.config["global_settings"].get("color_circle", "#FFFFFF")
        stroke_width = self.config["global_settings"].get("stroke_width", 2)
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
        
        circle = Circle(
            radius=radius,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity
        )
        return circle
    
    def get_fitted_image(self, scale_name, radius, image_index=0):
        """
        Load an image for a scale and fit it to a circle with proper masking
        
        Args:
            scale_name (str): Name of the scale
            radius (float): Radius of the circle
            image_index (int, optional): Index if multiple images are available
            
        Returns:
            Mobject: The circular masked image as a Manim mobject
        """
        image_path = self.get_image_for_scale(scale_name, image_index)
        if image_path:
            return self.create_circular_masked_image(image_path, radius)
        return self._create_fallback_circle(radius)
        
    def cleanup(self):
        """Clean up temporary files created during image processing"""
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                print(f"Error cleaning up temp file {file_path}: {e}")
        self._temp_files = []
        
    def __del__(self):
        """Destructor to ensure cleanup when the object is garbage collected"""
        self.cleanup()