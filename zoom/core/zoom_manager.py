"""
Zoom Manager for Universe Zoom Animation
Controls transitions between different scale scenes with truly smooth logarithmic scaling
"""

import os
import numpy as np
from manim import *
from manim.utils import rate_functions

# Define and ensure all necessary constants
# These will override any imported values if they exist,
# or define them if they don't exist in the imported namespace
UR = np.array([1.0, 1.0, 0.0])  # Upper right
UL = np.array([-1.0, 1.0, 0.0])  # Upper left
DL = np.array([-1.0, -1.0, 0.0])  # Down left
DR = np.array([1.0, -1.0, 0.0])  # Down right
UP = np.array([0.0, 1.0, 0.0])   # Up
DOWN = np.array([0.0, -1.0, 0.0])  # Down
RIGHT = np.array([1.0, 0.0, 0.0])  # Right
LEFT = np.array([-1.0, 0.0, 0.0])  # Left

# Define frame dimensions for manim
# Standard ManimCE default values
FRAME_WIDTH = 8
FRAME_HEIGHT = 4.5
FRAME_X_RADIUS = FRAME_WIDTH / 2
FRAME_Y_RADIUS = FRAME_HEIGHT / 2

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
        
        # For caching scene objects
        self._scene_instances = {}
        
        # For tracking resources that need cleanup
        self._active_mobjects = []
    
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
    
    def _create_scene_elements(self, scene_name, scene_obj):
        """
        Create elements for a scene
        
        Args:
            scene_name (str): The name of the scene
            scene_obj (ZoomableScene): The scene object
            
        Returns:
            Group: A group containing all the scene elements
        """
        print(f"Creating elements for scene: {scene_name}")
        
        # Create an empty Group (not VGroup, as Group can contain any Mobject)
        elements = Group()
        
        # Track for cleanup
        self._active_mobjects.append(elements)
        
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
                                # Track individual elements for cleanup
                                self._active_mobjects.append(element)
                        
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
        # Track for cleanup
        self._active_mobjects.extend([default_circle, default_label])
        elements = Group(default_circle, default_label)
        return elements
    
    def _get_or_create_scene(self, manim_scene, scene_name):
        """
        Get a cached scene instance or create a new one
        
        Args:
            manim_scene (Scene): The Manim scene object
            scene_name (str): The name of the scene
            
        Returns:
            ZoomableScene: A scene instance
        """
        # Check if we already have this scene instantiated
        if scene_name in self._scene_instances:
            return self._scene_instances[scene_name]
            
        if scene_name not in self.scenes:
            raise ValueError(f"Unknown scene: {scene_name}")
        
        scene_info = self.scenes[scene_name]
        scene_class = scene_info["class"]
        scale_value = scene_info["scale"]
        
        # Create a new instance of the scene class and set its parent scene
        scene_obj = scene_class(self.config, scale_value)
        scene_obj.parent_scene = manim_scene
        
        # Cache the instance
        self._scene_instances[scene_name] = scene_obj
        
        return scene_obj
    
    def _create_true_logarithmic_scale_updater(self, from_scale, to_scale, duration):
        """
        Create a smooth logarithmic scale updater function
        
        Args:
            from_scale (float): Starting scale value
            to_scale (float): Ending scale value
            duration (float): Duration of the animation
            
        Returns:
            function: A scale updater function for animating logarithmic transitions
        """
        # Create a value tracker for the logarithmic scale
        scale_tracker = ValueTracker(from_scale)
        
        # Create the scale indicator with correct initial value
        scale_indicator = Text(
            f"10^{from_scale} m",
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        ).to_corner(UR, buff=0.5)
        
        # Create the updater function that smoothly updates the indicator
        def update_scale_indicator(text):
            current_scale = scale_tracker.get_value()
            new_text = Text(
                f"10^{current_scale:.1f} m",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=self.config["global_settings"].get("color_text", "#FFFFFF")
            ).to_corner(UR, buff=0.5)
            text.become(new_text)
        
        # Add the updater to the indicator
        scale_indicator.add_updater(update_scale_indicator)
        
        return scale_indicator, scale_tracker
    
    def zoom_in(self, manim_scene, from_scene, to_scene, duration=None, easing="smooth"):
        """
        Handle zoom-in animation between scenes with true smooth logarithmic scaling
        
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
        
        print(f"Zoom in from {from_scene} (10^{from_scale}) to {to_scene} (10^{to_scale})")
        
        # Create scene objects
        from_scene_obj = self._get_or_create_scene(manim_scene, from_scene)
        to_scene_obj = self._get_or_create_scene(manim_scene, to_scene)
        
        # Create scene elements
        from_elements = self._create_scene_elements(from_scene, from_scene_obj)
        to_elements = self._create_scene_elements(to_scene, to_scene_obj)
        
        # Clear the scene
        manim_scene.clear()
        
        # Create background
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")
        background = Rectangle(
            width=FRAME_WIDTH * 4,  # Make it extra large to cover during zoom
            height=FRAME_HEIGHT * 4,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0
        )
        manim_scene.add(background)
        
        # Prepare from and to elements
        from_elements.move_to(ORIGIN)
        to_elements.move_to(ORIGIN)
        to_elements.scale(0.01)  # Start very small
        to_elements.set_opacity(0)  # Start invisible
        
        # Create scene labels
        scene_label = Text(
            from_scene,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        ).to_corner(UL, buff=0.5)
        
        # Create smooth logarithmic scale indicator
        scale_indicator, scale_tracker = self._create_true_logarithmic_scale_updater(
            from_scale, to_scale, duration
        )
        
        # Add everything to the scene
        manim_scene.add(from_elements, to_elements, scene_label, scale_indicator)
        
        # Calculate intermediate scale values for true smooth logarithmic scaling
        # Number of animated frames (60fps × duration)
        num_frames = int(60 * duration)
        
        # Determine the direction of scaling (zoom in = from larger to smaller objects)
        scale_diff = abs(to_scale - from_scale)
        
        # For zoom animations, we need to:
        # 1. Scale up the source object until it fills the screen
        # 2. Cross-fade to the destination object 
        # 3. Scale the destination object down to its proper size
        
        # Prepare animations
        from_final_scale = 40.0  # Scale up to large size, then fade out
        to_initial_scale = 0.01  # Start very small, grow to normal size
        
        # First half: grow from_elements and update scale
        first_half = duration * 0.5
        manim_scene.play(
            from_elements.animate.scale(from_final_scale),
            Transform(scene_label, 
                     Text(from_scene + " → " + to_scene,
                         font_size=self.config["global_settings"].get("font_size", 24),
                         color=self.config["global_settings"].get("color_text", "#FFFFFF"))
                     .to_corner(UL, buff=0.5)),
            scale_tracker.animate.set_value(from_scale + (to_scale - from_scale) * 0.5),
            run_time=first_half,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Cross-fade at midpoint
        manim_scene.play(
            from_elements.animate.set_opacity(0),
            to_elements.animate.set_opacity(1),
            run_time=0.3,
            rate_func=rate_functions.linear
        )
        
        # Second half: shrink to_elements and continue updating scale
        second_half = duration * 0.5
        manim_scene.play(
            to_elements.animate.scale(1/to_initial_scale),
            Transform(scene_label, 
                     Text(to_scene,
                         font_size=self.config["global_settings"].get("font_size", 24),
                         color=self.config["global_settings"].get("color_text", "#FFFFFF"))
                     .to_corner(UL, buff=0.5)),
            scale_tracker.animate.set_value(to_scale),
            run_time=second_half,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Remove updater from scale indicator
        scale_indicator.remove_updater(scale_indicator.get_updaters()[0])
        
        # Clean up the scene
        manim_scene.remove(from_elements)
        
        # Update the current scene and scale
        self.current_scene = to_scene
        self.current_scale = to_scale
    
    def zoom_out(self, manim_scene, from_scene, to_scene, duration=None, easing="smooth"):
        """
        Handle zoom-out animation between scenes with true smooth logarithmic scaling
        
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
        
        print(f"Zoom out from {from_scene} (10^{from_scale}) to {to_scene} (10^{to_scale})")
        
        # Create scene objects
        from_scene_obj = self._get_or_create_scene(manim_scene, from_scene)
        to_scene_obj = self._get_or_create_scene(manim_scene, to_scene)
        
        # Create scene elements
        from_elements = self._create_scene_elements(from_scene, from_scene_obj)
        to_elements = self._create_scene_elements(to_scene, to_scene_obj)
        
        # Clear the scene
        manim_scene.clear()
        
        # Create background
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")
        background = Rectangle(
            width=FRAME_WIDTH * 4,  # Make it extra large to cover during zoom
            height=FRAME_HEIGHT * 4,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0
        )
        manim_scene.add(background)
        
        # Prepare from and to elements
        from_elements.move_to(ORIGIN)
        to_elements.move_to(ORIGIN)
        to_elements.scale(100)  # Start very large
        to_elements.set_opacity(0)  # Start invisible
        
        # Create scene labels
        scene_label = Text(
            from_scene,
            font_size=self.config["global_settings"].get("font_size", 24),
            color=self.config["global_settings"].get("color_text", "#FFFFFF")
        ).to_corner(UL, buff=0.5)
        
        # Create smooth logarithmic scale indicator
        scale_indicator, scale_tracker = self._create_true_logarithmic_scale_updater(
            from_scale, to_scale, duration
        )
        
        # Add everything to the scene
        manim_scene.add(from_elements, to_elements, scene_label, scale_indicator)
        
        # For zoom out, we:
        # 1. Shrink the source object until it's very small
        # 2. Cross-fade to the destination object which starts large
        # 3. Scale the destination object down to its proper size
        
        # Prepare animations
        from_final_scale = 0.01  # Shrink from normal to tiny
        to_initial_scale = 100  # Start very large, shrink to normal
        
        # First half: shrink from_elements and update scale
        first_half = duration * 0.5
        manim_scene.play(
            from_elements.animate.scale(from_final_scale),
            Transform(scene_label, 
                     Text(from_scene + " → " + to_scene,
                         font_size=self.config["global_settings"].get("font_size", 24),
                         color=self.config["global_settings"].get("color_text", "#FFFFFF"))
                     .to_corner(UL, buff=0.5)),
            scale_tracker.animate.set_value(from_scale + (to_scale - from_scale) * 0.5),
            run_time=first_half,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Cross-fade at midpoint
        manim_scene.play(
            from_elements.animate.set_opacity(0),
            to_elements.animate.set_opacity(1),
            run_time=0.3,
            rate_func=rate_functions.linear
        )
        
        # Second half: shrink to_elements and continue updating scale
        second_half = duration * 0.5
        manim_scene.play(
            to_elements.animate.scale(1/to_initial_scale),
            Transform(scene_label, 
                     Text(to_scene,
                         font_size=self.config["global_settings"].get("font_size", 24),
                         color=self.config["global_settings"].get("color_text", "#FFFFFF"))
                     .to_corner(UL, buff=0.5)),
            scale_tracker.animate.set_value(to_scale),
            run_time=second_half,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Remove updater from scale indicator
        scale_indicator.remove_updater(scale_indicator.get_updaters()[0])
        
        # Clean up the scene
        manim_scene.remove(from_elements)
        
        # Update the current scene and scale
        self.current_scene = to_scene
        self.current_scale = to_scale
    
    def cleanup_resources(self):
        """
        Clean up resources to prevent memory and semaphore leaks
        """
        print("Cleaning up active mobjects...")
        # Clear references to active mobjects
        self._active_mobjects.clear()
        
        # Clear scene instance cache
        self._scene_instances.clear()
        
        # Explicitly run garbage collection
        import gc
        gc.collect()
        
        print("Resource cleanup completed")
        
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
        
        print(f"Starting animation sequence with {len(self.config['animation_sequence'])} transitions")
        
        try:
            # Process each animation in the sequence
            for i, transition in enumerate(self.config["animation_sequence"]):
                print(f"Processing transition {i+1}/{len(self.config['animation_sequence'])}")
                
                from_scene = transition["from_scene"]
                to_scene = transition["to_scene"]
                direction = transition.get("direction", "in").lower()
                duration = transition.get("duration", 5)
                easing_function = transition.get("easing_function", "smooth")
                pause_before = transition.get("pause_before", 0)
                pause_after = transition.get("pause_after", 0)
                
                # Check if we should show scale indicator
                show_scale = transition.get("scale_indicator_visible", True)
                
                # Wait before animation if needed
                if pause_before > 0:
                    print(f"Pausing for {pause_before} seconds before animation")
                    manim_scene.wait(pause_before)
                    current_time += pause_before
                    
                    # Play narration if scheduled for this time
                    self.audio_controller.check_narration_cues(current_time)
                
                # Perform the animation
                print(f"Animating {direction} from {from_scene} to {to_scene} over {duration} seconds")
                if direction == "in":
                    self.zoom_in(manim_scene, from_scene, to_scene, duration, easing_function)
                else:
                    self.zoom_out(manim_scene, from_scene, to_scene, duration, easing_function)
                
                current_time += duration
                
                # Play narration if scheduled for this time
                self.audio_controller.check_narration_cues(current_time)
                
                # Wait after animation if needed
                if pause_after > 0:
                    print(f"Pausing for {pause_after} seconds after animation")
                    manim_scene.wait(pause_after)
                    current_time += pause_after
                    
                    # Play narration if scheduled for this time
                    self.audio_controller.check_narration_cues(current_time)
            
            print("Animation sequence completed")
        finally:
            # Stop audio
            self.audio_controller.stop_all()
            
            # Clean up resources to prevent leaks
            self.cleanup_resources()