"""
Base scene implementation for NPQG Universe Zoom Animation
All specific scene types inherit from this base class
"""

from manim import *

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
        
    def setup(self):
        """Initialize scene components"""
        self.setup_background()
        self.setup_scale_indicator()
        
    def setup_background(self):
        """Create the background with the configured color"""
        # Extract settings from config
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")  # Default to INDIGO
        
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
        self.add(self.background)
        
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
            font_size=font_size,
            color=text_color
        )
        
        # Position in top right corner with padding
        self.scale_indicator.to_corner(UR, buff=0.5)
        self.add(self.scale_indicator)
        
    def create_object(self, label, position, radius):
        """
        Create a circle with a label at the specified position
        
        Args:
            label (str): The label text for the object
            position (list): The [x, y, z] position coordinates
            radius (float): The radius of the circle
            
        Returns:
            VGroup: A group containing the circle and label
        """
        # Extract settings from config
        stroke_width = self.config["global_settings"].get("stroke_width", 2)
        circle_color = self.config["global_settings"].get("color_circle", "#FFFFFF")
        font_size = self.config["global_settings"].get("font_size", 24)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        
        # Convert position list to 3D array if needed
        if isinstance(position, list):
            if len(position) == 2:
                position = [position[0], position[1], 0]
            position = np.array(position)
        
        # Create the circle
        circle = Circle(
            radius=radius,
            stroke_color=circle_color,
            stroke_width=stroke_width,
            fill_opacity=0
        )
        circle.move_to(position)
        
        # Create the label
        label_text = Text(
            label,
            font_size=font_size,
            color=text_color
        )
        label_text.move_to(position)
        
        # Group the circle and label
        obj = VGroup(circle, label_text)
        self.objects.append(obj)
        self.add(obj)
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