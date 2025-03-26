"""
Zoom Manager for NPQG Universe Zoom Animation
Controls transitions between different scale scenes
"""

import numpy as np
from manim import *
from manim.utils import rate_functions

# Define directional constants if not available in this version of Manim
try:
    from manim.constants import *
except (ImportError, AttributeError):
    # Define our own constants if they don't exist
    UR = np.array([1.0, 1.0, 0.0])  # Upper right
    UL = np.array([-1.0, 1.0, 0.0])  # Upper left
    DL = np.array([-1.0, -1.0, 0.0])  # Down left
    DR = np.array([1.0, -1.0, 0.0])  # Down right
    UP = np.array([0.0, 1.0, 0.0])   # Up
    DOWN = np.array([0.0, -1.0, 0.0])  # Down
    RIGHT = np.array([1.0, 0.0, 0.0])  # Right
    LEFT = np.array([-1.0, 0.0, 0.0])  # Left

from scenes.base_scene import ZoomableScene
from scenes.universe_scene import UniverseScene
from scenes.galaxy_cluster_scene import GalaxyClusterScene
from scenes.galaxy_scene import GalaxyScene
from scenes.black_hole_scene import BlackHoleScene
from scenes.solar_system_scene import SolarSystemScene
from scenes.star_scene import StarScene
from scenes.molecule_scene import MoleculeScene
from scenes.atom_scene import AtomScene
from scenes.electron_scene import ElectronScene
from scenes.quark_scene import QuarkScene
from scenes.point_potential_scene import PointPotentialScene
from core.audio_controller import AudioController

class ZoomManager:
    """Manages scene transitions and zoom animations"""
    
    def __init__(self, config):
        """
        Initialize the zoom manager
        
        Args:
            config (dict): The configuration data from the JSON file
        """
        self.config = config
        self.scenes = {}
        self.current_scene = None
        self.current_scale = None
        self.animation_progress = 0
        self.total_duration = self._calculate_total_duration()
        self.audio_controller = AudioController(self.config.get("audio", {}))
        
        # Initialize the scenes
        self._initialize_scenes()
    
    def _initialize_scenes(self):
        """Create all scene instances based on the configuration"""
        for scene_config in self.config["scenes"]:
            scene_name = scene_config["name"]
            scale_value = scene_config["scale"]
            
            # Create the appropriate scene type based on name
            if scene_name == "Universe":
                scene_class = UniverseScene
            elif scene_name == "GalaxyCluster":
                scene_class = GalaxyClusterScene
            elif scene_name == "Galaxy":
                scene_class = GalaxyScene
            elif scene_name == "BlackHole":
                scene_class = BlackHoleScene
            elif scene_name == "SolarSystem":
                scene_class = SolarSystemScene
            elif scene_name == "Star":
                scene_class = StarScene
            elif scene_name == "Molecule":
                scene_class = MoleculeScene
            elif scene_name == "Atom":
                scene_class = AtomScene
            elif scene_name == "Electron":
                scene_class = ElectronScene
            elif scene_name == "Quark":
                scene_class = QuarkScene
            elif scene_name == "PointPotential":
                scene_class = PointPotentialScene
            else:
                # Use generic scene as fallback
                scene_class = ZoomableScene
            
            # Store the scene class and config for later instantiation
            self.scenes[scene_name] = {
                "class": scene_class,
                "scale": scale_value,
                "config": scene_config
            }
    
    def _calculate_total_duration(self):
        """Calculate the total animation duration including transitions and pauses"""
        total = 0
        for transition in self.config["animation_sequence"]:
            duration = transition.get("duration", 5)
            pause_before = transition.get("pause_before", 0)
            pause_after = transition.get("pause_after", 0)
            total += duration + pause_before + pause_after
        return total
    
    def _apply_easing(self, t, easing_type):
        """
        Apply easing function to create smoother animations
        
        Args:
            t (float): Animation progress from 0 to 1
            easing_type (str): Easing function type
            
        Returns:
            float: Eased value between 0 and 1
        """
        if easing_type == "linear":
            return t
        elif easing_type == "smooth":
            # Smooth step function (3t² - 2t³)
            return 3 * t**2 - 2 * t**3
        elif easing_type == "accelerate":
            # Quadratic ease-in
            return t**2
        elif easing_type == "decelerate":
            # Quadratic ease-out
            return 1 - (1 - t)**2
        else:
            return t  # Default to linear
    
    def _create_scene_elements(self, scene_name, scene_obj):
        """
        Create elements for a scene
        
        Args:
            scene_name (str): The name of the scene
            scene_obj (ZoomableScene): The scene object
            
        Returns:
            VGroup: A group containing all the scene elements
        """
        print(f"Creating elements for scene: {scene_name}")
        
        # Create default elements (as a fallback)
        default_circle = Circle(
            radius=3,
            stroke_color=WHITE,
            fill_opacity=0
        )
        default_label = Text(
            scene_name,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=WHITE
        )
        
        # Create an empty Group (not VGroup, as Group can contain any Mobject)
        elements = Group()
        
        # Try to get custom elements
        try:
            if hasattr(scene_obj, "get_elements") and callable(scene_obj.get_elements):
                print(f"Scene {scene_name} has get_elements method")
                
                try:
                    custom_elements = scene_obj.get_elements()
                    if custom_elements and isinstance(custom_elements, list) and len(custom_elements) > 0:
                        # Add each custom element
                        print(f"Adding {len(custom_elements)} custom elements")
                        for element in custom_elements:
                            if element is not None:
                                elements.add(element)
                        
                        # If we successfully added elements, return them
                        if len(elements.submobjects) > 0:
                            print(f"Successfully created custom elements for {scene_name}")
                            return elements
                except Exception as e:
                    print(f"Error calling get_elements for {scene_name}: {e}")
        except Exception as e:
            print(f"Error checking for get_elements method: {e}")
        
        # If we reach here, use default elements
        print(f"Using default elements for {scene_name}")
        elements = Group(default_circle, default_label)
        return elements
    
    def zoom_in(self, manim_scene, from_scene, to_scene, duration=None, easing="smooth"):
        """
        Handle zoom-in animation between scenes
        
        Args:
            manim_scene (Scene): The Manim scene object
            from_scene (str): The name of the starting scene
            to_scene (str): The name of the target scene
            duration (float, optional): Animation duration in seconds
            easing (str, optional): Easing function type
        """
        if duration is None:
            duration = self.config["global_settings"].get("default_zoom_rate", 5)
        
        # Get the scene scale values
        from_scale = self.scenes[from_scene]["scale"]
        to_scale = self.scenes[to_scene]["scale"]
        scale_diff = abs(from_scale - to_scale)
        
        # Create the scenes if they don't exist
        from_scene_obj = self._get_or_create_scene(manim_scene, from_scene)
        to_scene_obj = self._get_or_create_scene(manim_scene, to_scene)
        
        # Setup variables for the animation
        start_scale = from_scale
        end_scale = to_scale
        
        # Clear the scene and create the initial elements
        manim_scene.clear()
        
        # Create background
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")
        width = self.config["global_settings"].get("resolution", [1920, 1080])[0] / 100
        height = self.config["global_settings"].get("resolution", [1920, 1080])[1] / 100
        
        background = Rectangle(
            width=width * 4,  # Make it extra large to cover during zoom
            height=height * 4,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0
        )
        manim_scene.add(background)
        
        print(f"Creating scene elements for zoom-in from {from_scene} to {to_scene}")
        
        # Create scene elements using helper method
        try:
            from_elements = self._create_scene_elements(from_scene, from_scene_obj)
            to_elements = self._create_scene_elements(to_scene, to_scene_obj)
        except Exception as e:
            print(f"Error creating scene elements: {e}")
            # Create basic fallback elements
            from_elements = Group(
                Circle(radius=3, stroke_color=WHITE),
                Text(from_scene, color=WHITE)
            )
            to_elements = Group(
                Circle(radius=3, stroke_color=WHITE),
                Text(to_scene, color=WHITE)
            )
        
        # Position to_elements off-screen or invisible initially
        to_elements.scale(0.1)  # Small enough to be barely visible
        to_elements.set_opacity(0)  # Start invisible
        
        # Create scene labels in top left
        from_scene_label = Text(
            from_scene,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        from_scene_label.to_corner(UP + LEFT, buff=0.5)
        
        to_scene_label = Text(
            to_scene,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        to_scene_label.to_corner(UP + LEFT, buff=0.5)
        to_scene_label.set_opacity(0)  # Start invisible
        
        # Create transition text
        transition_text = Text(
            f"Zooming in: {from_scene} → {to_scene}",
            font_size=self.config["global_settings"].get("font_size", 20),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        transition_text.to_edge(UP, buff=0.1)
        
        # Create scale indicators in top right
        from_scale_indicator = Text(
            f"10^{start_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        from_scale_indicator.to_corner(UP + RIGHT, buff=0.5)
        
        to_scale_indicator = Text(
            f"10^{end_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        to_scale_indicator.to_corner(UP + RIGHT, buff=0.5)
        to_scale_indicator.set_opacity(0)  # Start invisible
        
        # Add all elements to the scene
        manim_scene.add(from_elements, to_elements, from_scale_indicator, to_scale_indicator,
                       from_scene_label, to_scene_label, transition_text)
        
        print("Starting zoom-in animation")
        
        # Create the zoom-in animation
        # Note: We need to separate animations as Manim may not handle multiple transforms on same object
        
        # Create a simplified continuous scale indicator
        # Create a value tracker for the logarithmic scale
        scale_value_tracker = ValueTracker(from_scale)
        
        # Create dynamic scale indicator
        scale_indicator = Text(
            f"10^{from_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        ).to_corner(UP + RIGHT, buff=0.5)
        
        # Function to update scale text
        def update_scale_text(text):
            new_scale = scale_value_tracker.get_value()
            new_text = Text(
                f"10^{new_scale:.1f} m",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=self.config["global_settings"].get("color_text", "#FFFFFF")
            ).to_corner(UP + RIGHT, buff=0.5)
            text.become(new_text)
        
        # Add updater to scale indicator
        scale_indicator.add_updater(update_scale_text)
        
        # Replace static indicators with dynamic one
        manim_scene.remove(from_scale_indicator, to_scale_indicator)
        manim_scene.add(scale_indicator)
        
        # Calculate target scale for scaling animations
        # For a zoom-in effect (from larger to smaller scale view)
        zoom_scale_factor = 5  # Empirically determined for good visual effect
        
        # First animate scaling up and fading out from_elements
        manim_scene.play(
            from_elements.animate.scale(zoom_scale_factor).set_opacity(0),
            from_scene_label.animate.set_opacity(0),
            scale_value_tracker.animate.set_value(from_scale + (to_scale - from_scale) * 0.5),
            rate_func=rate_functions.ease_in_out_sine,
            run_time=duration/2
        )
        
        # Then animate the to_elements appearing and scaling to normal
        manim_scene.play(
            to_elements.animate.scale(1/zoom_scale_factor).set_opacity(1),
            to_scene_label.animate.set_opacity(1),
            scale_value_tracker.animate.set_value(to_scale),
            rate_func=rate_functions.ease_in_out_sine,
            run_time=duration/2
        )
        
        # Remove updater to prevent further updates
        scale_indicator.remove_updater(update_scale_text)
        
        print("Zoom-in animation completed")
        
        # Clean up: remove from_elements and old indicators/labels
        manim_scene.remove(from_elements, from_scale_indicator, from_scene_label)
        
        # Update the current scene and scale
        self.current_scene = to_scene
        self.current_scale = to_scale
    
    def zoom_out(self, manim_scene, from_scene, to_scene, duration=None, easing="smooth"):
        """
        Handle zoom-out animation between scenes
        
        Args:
            manim_scene (Scene): The Manim scene object
            from_scene (str): The name of the starting scene
            to_scene (str): The name of the target scene
            duration (float, optional): Animation duration in seconds
            easing (str, optional): Easing function type
        """
        if duration is None:
            duration = self.config["global_settings"].get("default_zoom_rate", 5)
        
        # Get the scene scale values
        from_scale = self.scenes[from_scene]["scale"]
        to_scale = self.scenes[to_scene]["scale"]
        scale_diff = abs(from_scale - to_scale)
        
        # Create the scenes if they don't exist
        from_scene_obj = self._get_or_create_scene(manim_scene, from_scene)
        to_scene_obj = self._get_or_create_scene(manim_scene, to_scene)
        
        # Setup variables for the animation
        start_scale = from_scale
        end_scale = to_scale
        
        # Clear the scene and create the initial elements
        manim_scene.clear()
        
        # Create background
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")
        width = self.config["global_settings"].get("resolution", [1920, 1080])[0] / 100
        height = self.config["global_settings"].get("resolution", [1920, 1080])[1] / 100
        
        background = Rectangle(
            width=width * 4,  # Make it extra large to cover during zoom
            height=height * 4,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0
        )
        manim_scene.add(background)
        
        print(f"Creating scene elements for zoom-out from {from_scene} to {to_scene}")
        
        # Create scene elements using helper method
        try:
            from_elements = self._create_scene_elements(from_scene, from_scene_obj)
            to_elements = self._create_scene_elements(to_scene, to_scene_obj)
        except Exception as e:
            print(f"Error creating scene elements: {e}")
            # Create basic fallback elements
            from_elements = Group(
                Circle(radius=3, stroke_color=WHITE),
                Text(from_scene, color=WHITE)
            )
            to_elements = Group(
                Circle(radius=3, stroke_color=WHITE),
                Text(to_scene, color=WHITE)
            )
        
        # Initially, to_elements should be large (we'll shrink it)
        to_elements.scale(5)  # Large enough to be off screen
        to_elements.set_opacity(0)  # Start invisible
        
        # Create scene labels in top left
        from_scene_label = Text(
            from_scene,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        from_scene_label.to_corner(UP + LEFT, buff=0.5)
        
        to_scene_label = Text(
            to_scene,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        to_scene_label.to_corner(UP + LEFT, buff=0.5)
        to_scene_label.set_opacity(0)  # Start invisible
        
        # Create transition text
        transition_text = Text(
            f"Zooming out: {from_scene} → {to_scene}",
            font_size=self.config["global_settings"].get("font_size", 20),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        transition_text.to_edge(UP, buff=0.1)
        
        # Create scale indicators in top right
        from_scale_indicator = Text(
            f"10^{start_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        from_scale_indicator.to_corner(UP + RIGHT, buff=0.5)
        
        to_scale_indicator = Text(
            f"10^{end_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        )
        to_scale_indicator.to_corner(UP + RIGHT, buff=0.5)
        to_scale_indicator.set_opacity(0)  # Start invisible
        
        # Add all elements to the scene
        manim_scene.add(from_elements, to_elements, from_scale_indicator, to_scale_indicator,
                       from_scene_label, to_scene_label, transition_text)
        
        print("Starting zoom-out animation")
        
        # Create a simplified continuous scale indicator
        # Create a value tracker for the logarithmic scale
        scale_value_tracker = ValueTracker(from_scale)
        
        # Create dynamic scale indicator
        scale_indicator = Text(
            f"10^{from_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        ).to_corner(UP + RIGHT, buff=0.5)
        
        # Function to update scale text
        def update_scale_text(text):
            new_scale = scale_value_tracker.get_value()
            new_text = Text(
                f"10^{new_scale:.1f} m",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=self.config["global_settings"].get("color_text", "#FFFFFF")
            ).to_corner(UP + RIGHT, buff=0.5)
            text.become(new_text)
        
        # Add updater to scale indicator
        scale_indicator.add_updater(update_scale_text)
        
        # Replace static indicators with dynamic one
        manim_scene.remove(from_scale_indicator, to_scale_indicator)
        manim_scene.add(scale_indicator)
        
        # Calculate target scale for scaling animations
        # For a zoom-out effect (from smaller to larger scale view)
        zoom_scale_factor = 0.2  # Empirically determined for good visual effect
        
        # First animate scaling down and fading out from_elements
        manim_scene.play(
            from_elements.animate.scale(zoom_scale_factor).set_opacity(0),
            from_scene_label.animate.set_opacity(0),
            scale_value_tracker.animate.set_value(from_scale + (to_scale - from_scale) * 0.5),
            rate_func=rate_functions.ease_in_out_sine,
            run_time=duration/2
        )
        
        # Prepare to_elements to start large
        to_elements.scale(1/zoom_scale_factor)
        to_elements.set_opacity(0)
        
        # Then animate the to_elements appearing and scaling to normal
        manim_scene.play(
            to_elements.animate.scale(zoom_scale_factor).set_opacity(1),
            to_scene_label.animate.set_opacity(1),
            scale_value_tracker.animate.set_value(to_scale),
            rate_func=rate_functions.ease_in_out_sine,
            run_time=duration/2
        )
        
        # Remove updater to prevent further updates
        scale_indicator.remove_updater(update_scale_text)
        
        print("Zoom-out animation completed")
        
        # Clean up: remove from_elements and old indicators/labels
        manim_scene.remove(from_elements, from_scale_indicator, from_scene_label)
        
        # Update the current scene and scale
        self.current_scene = to_scene
        self.current_scale = to_scale
    
    def _get_or_create_scene(self, manim_scene, scene_name):
        """
        Get or create a scene instance
        
        Args:
            manim_scene (Scene): The Manim scene object
            scene_name (str): The name of the scene
            
        Returns:
            ZoomableScene: A scene instance
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Unknown scene: {scene_name}")
        
        scene_info = self.scenes[scene_name]
        scene_class = scene_info["class"]
        scale_value = scene_info["scale"]
        
        # Create a new instance of the scene class and set its parent scene
        scene_obj = scene_class(self.config, scale_value)
        
        # Instead of directly setting the camera, we'll use the parent scene for camera operations
        scene_obj.parent_scene = manim_scene
        
        return scene_obj
    
    def execute_animation_sequence(self, manim_scene):
        """
        Run the full animation sequence defined in config
        
        Args:
            manim_scene (Scene): The Manim scene object
        """
        current_time = 0
        
        # Configure the camera background color
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")
        try:
            manim_scene.camera.background_color = bg_color
        except:
            # Some Manim versions don't allow setting background_color directly
            print(f"Note: Could not set camera background color directly")
        
        # Start audio if configured
        if self.config.get("audio", {}).get("background_music"):
            self.audio_controller.start_background_music()
        
        # Process each transition in the sequence
        for i, transition in enumerate(self.config["animation_sequence"]):
            from_scene_name = transition["from_scene"]
            to_scene_name = transition["to_scene"]
            direction = transition.get("direction", "in")
            duration = transition.get("duration", 5)
            easing = transition.get("easing_function", "smooth")
            pause_before = transition.get("pause_before", 0)
            pause_after = transition.get("pause_after", 0)
            
            # Log the current transition for debugging
            print(f"Animating: {from_scene_name} -> {to_scene_name} ({direction})")
            
            # Apply pause before if specified
            if pause_before > 0:
                print(f"Waiting {pause_before}s before transition")
                manim_scene.wait(pause_before)
                current_time += pause_before
                
                # Check for narration during pause
                self.audio_controller.check_narration_cues(current_time)
            
            # Execute the transition
            try:
                print(f"Preparing to execute {direction} transition from {from_scene_name} to {to_scene_name}")
                
                if direction == "in":
                    print("Starting zoom-in transition")
                    self.zoom_in(
                        manim_scene, 
                        from_scene_name, 
                        to_scene_name, 
                        duration, 
                        easing
                    )
                    print("Zoom-in transition completed")
                else:  # "out"
                    print("Starting zoom-out transition")
                    self.zoom_out(
                        manim_scene, 
                        from_scene_name, 
                        to_scene_name, 
                        duration, 
                        easing
                    )
                    print("Zoom-out transition completed")
                    
                current_time += duration
                
                # Check for narration during transition
                self.audio_controller.check_narration_cues(current_time)
            except Exception as e:
                import traceback
                print(f"Error during {direction} transition: {e}")
                print("Detailed traceback:")
                traceback.print_exc()
                
                # Create a text message about the error
                error_text = Text(
                    f"Error during {direction} transition",
                    color=RED
                )
                manim_scene.add(error_text)
                manim_scene.wait(2)
                manim_scene.remove(error_text)
                
            # Apply pause after if specified
            if pause_after > 0:
                print(f"Waiting {pause_after}s after transition")
                manim_scene.wait(pause_after)
                current_time += pause_after
                
                # Check for narration during pause
                self.audio_controller.check_narration_cues(current_time)
                
        # Display final message
        print(f"Animation sequence completed in {current_time}s")