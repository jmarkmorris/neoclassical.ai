#!/usr/bin/env python3
"""
NPQG Universe Zoom Animation
- Labels positioned next to circles
- Labels zoom with circles
- Circles and labels dissolve at 95% of frame height
- Continuous zooming without pauses
- Integer-only scale indicators
"""

from manim import *
import json
import os
import sys
import numpy as np

# Define colors
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
WHITE = "#FFFFFF"
DEFAULT_BACKGROUND_COLOR = INDIGO

class ZoomAnimation(Scene):
    def construct(self):
        # Load config relative to this script's location
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, "zoom_config.json")
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            print(f"Please ensure 'zoom_config.json' is in the same directory as zoom.py.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {config_path}")
            sys.exit(1)

        # Set the background color
        self.camera.background_color = DEFAULT_BACKGROUND_COLOR

        # Get frame dimensions directly from the camera
        FRAME_WIDTH = self.camera.frame_width
        FRAME_HEIGHT = self.camera.frame_height

        # Extract scenes from config
        scenes = []
        for scene_config in self.config["scenes"]:
            scenes.append({
                "name": scene_config["name"],
                "scale": scene_config["scale"]
            })
        
        # Create animation sequence
        animation_sequence = self.config["animation_sequence"]
        
        # Process each transition
        for i, transition in enumerate(animation_sequence):
            from_scene = transition["from_scene"]
            to_scene = transition["to_scene"]
            direction = transition.get("direction", "in").lower()
            
            # Find the from and to scenes
            from_scene_data = next((s for s in scenes if s["name"] == from_scene), None)
            to_scene_data = next((s for s in scenes if s["name"] == to_scene), None)
            
            if not from_scene_data or not to_scene_data:
                print(f"Error: Could not find scene data for {from_scene} or {to_scene}")
                continue
            
            from_scale = from_scene_data["scale"]
            to_scale = to_scene_data["scale"]

            # Use fixed duration if specified in global settings
            fixed_duration = self.config["global_settings"].get("fixed_transition_duration")

            if fixed_duration is not None and fixed_duration > 0:
                duration = fixed_duration
            else:
                # Fallback to scale-based calculation if fixed duration is not set
                scale_diff = abs(to_scale - from_scale)
                secs_per_decade = self.config["global_settings"].get("scale_seconds_per_decade", 3.0)
                min_duration = self.config["global_settings"].get("min_transition_duration", 4.0)
                max_duration = self.config["global_settings"].get("max_transition_duration", 15.0)

                duration = scale_diff * secs_per_decade
                duration = max(min_duration, min(max_duration, duration))

            # Allow individual transitions to override the duration
            if "duration" in transition and transition["duration"] is not None:
                duration = transition["duration"]

            print(f"Animating {direction} from {from_scene} (10^{int(round(from_scale))}) to {to_scene} (10^{int(round(to_scale))}), Duration: {duration:.2f}s")

            if i == 0:
                # For the first transition, initialize the scene
                self._setup_scene(from_scene, from_scale, to_scene, to_scale)
            
            # Perform the zoom animation using demo-like approach
            if direction == "in":
                self._zoom_in(from_scene, to_scene, from_scale, to_scale, duration)
            else:
                self._zoom_out(from_scene, to_scene, from_scale, to_scale, duration)
            
    
    def _setup_scene(self, from_scene, from_scale, to_scene, to_scale):
        """Set up the initial scene with first circle and scale indicator"""
        # Set the background color
        self.camera.background_color = DEFAULT_BACKGROUND_COLOR

        # Get frame dimensions directly from the camera
        FRAME_WIDTH = self.camera.frame_width
        FRAME_HEIGHT = self.camera.frame_height

        # Create background - similar to the demo
        # The problem was here: the config was being used, not the DEFAULT_BACKGROUND_COLOR
        background = Rectangle(
            width=FRAME_WIDTH * 2,
            height=FRAME_HEIGHT * 2,
            fill_color=DEFAULT_BACKGROUND_COLOR,
            fill_opacity=1.0,
            stroke_width=0,
            z_index=-10
        )
        self.add(background)

        # Create the initial circle using the demo's approach
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)

        # Calculate target radius based on frame height
        target_radius = 0.9 * self.camera.frame_height / 2

        self.current_circle = Circle(
            radius=target_radius, # Set initial radius to target size
            stroke_color=WHITE,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )
        
        # Create label for the circle - positioned to the right
        font_size = self.config["global_settings"].get("font_size", 36)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        
        self.current_label = Text(
            from_scene,
            font="Arial",
            font_size=font_size,
            color=text_color,
            z_index=2  # Higher z-index to stay on top
        ).to_corner(UL, buff=0.5) # Position in top-left corner

        # Create scale indicator using scientific notation
        scale_value_sci = f"{10**from_scale:.1e}"
        self.scale_indicator = Text(
            f"{scale_value_sci} m",
            font="Arial",
            font_size=font_size,
            color=text_color
        ).to_corner(UR, buff=0.5)
        
        # Add initial elements to scene
        self.add(self.current_circle, self.current_label, self.scale_indicator)
    
    def _zoom_in(self, from_scene, to_scene, from_scale, to_scale, duration):
        """Perform a zoom-in transition"""
        # Get settings from config
        font_size = self.config["global_settings"].get("font_size", 36)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
        
        # Store current elements
        from_circle = self.current_circle
        from_label = self.current_label
        
        # Create the next (smaller) circle with a color variation
        next_fill_color = "#CC3366"  # Use a different color like in the demo
        initial_to_radius = 0.01 # Start very small
        to_circle = Circle(
            radius=initial_to_radius,
            stroke_color=WHITE,
            fill_color=next_fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )
        
        # Create the next label with a higher z-index to ensure it's above other elements
        to_label = Text(
            to_scene,
            font="Arial",
            font_size=font_size,
            color=text_color,
            z_index=5  # Very high z-index to ensure it stays on top
        ).to_corner(UL, buff=0.5) # Position in top-left corner

        # Position the new label above the screen initially
        to_label.shift(UP * 2)

        # Add new circle and the off-screen label to the scene
        self.add(to_circle, to_label)

        # Define frame height threshold for dissolve (90% of frame height)
        FRAME_HEIGHT = self.camera.frame_height # Use camera attribute
        frame_height_threshold = FRAME_HEIGHT * 0.90 # Use 90%

        # Updater for first circle - dissolve when too large
        def update_from_circle(circle):
            # Calculate circle size relative to frame
            circle_relative_size = circle.height / self.camera.frame_height # Use camera attribute
            # Dissolve when circle exceeds threshold (90%)
            if circle_relative_size >= frame_height_threshold:
                # Calculate how far into dissolve we are (relative to the 90% threshold)
                exceeded_by = circle_relative_size - frame_height_threshold
                # Dissolve over a certain range (e.g., from 90% to 110% size)
                dissolve_range = 0.2 # Corresponds to 20% of frame height
                dissolve_progress = min(1.0, exceeded_by / dissolve_range)
                circle.set_opacity(max(0, 1.0 - dissolve_progress))

        # Create a ValueTracker for the scale
        scale_tracker = ValueTracker(from_scale)

        # Updater for scale indicator using the ValueTracker
        def update_scale(indicator):
            # Get the current scale from the tracker
            current_scale = scale_tracker.get_value()

            # Format scale using scientific notation
            scale_value_sci = f"{10**current_scale:.1e}"

            # Create new indicator with updated scale
            new_indicator = Text(
                f"{scale_value_sci} m",
                font="Arial",
                font_size=font_size,
                color=text_color
            ).to_corner(UR, buff=0.5)
            
            indicator.become(new_indicator)

        # Add the updaters for circle and scale
        from_circle.add_updater(update_from_circle)
        self.scale_indicator.add_updater(update_scale)

        # Calculate target radius and required scale factor for to_circle
        target_radius = 0.9 * self.camera.frame_height / 2
        target_scale_factor = target_radius / initial_to_radius

        # Create continuous animation - with larger scale and new label animation
        self.play(
            from_circle.animate.scale(20),              # Zoom first circle to be very large (dissolves anyway)
            to_circle.animate.scale(target_scale_factor), # Grow second circle to target size
            from_label.animate.shift(LEFT * 4),         # Move old label left off-screen
            to_label.animate.shift(DOWN * 2),           # Move new label down into place
            scale_tracker.animate.set_value(to_scale),  # Animate the scale value
            run_time=duration,
            rate_func=rate_functions.ease_in_out_sine
        )

        # Remove updaters
        from_circle.remove_updater(update_from_circle)
        self.scale_indicator.remove_updater(update_scale)

        # Clean up old circle and label objects
        self.remove(from_circle, from_label)

        # Update current objects
        self.current_circle = to_circle
        self.current_label = to_label
    
    def _zoom_out(self, from_scene, to_scene, from_scale, to_scale, duration):
        """Perform a zoom-out transition"""
        # Get settings from config
        font_size = self.config["global_settings"].get("font_size", 36)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        
        # Use a different color for each scale level, alternating between two colors
        if from_scene == "Universe":
            fill_color = "#3366CC"  # Blue
        else:
            fill_color = "#CC3366"  # Pink
            
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)

        # Store current elements
        from_circle = self.current_circle
        from_label = self.current_label

        # Calculate target radius
        target_radius = 0.9 * self.camera.frame_height / 2

        # Create the larger circle that we're zooming out to
        # Start it large enough to be off-screen initially
        initial_to_radius = target_radius * 20 # e.g., 20 times the final size
        to_circle = Circle(
            radius=initial_to_radius,
            stroke_color=WHITE,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )

        # Set initial state (already large radius, just set opacity)
        to_circle.set_opacity(0)  # Start invisible

        # Create the label for the larger circle with high z-index
        to_label = Text(
            to_scene,
            font="Arial",
            font_size=font_size,
            color=text_color,
            z_index=5  # Very high z-index to ensure it stays on top
        ).to_corner(UL, buff=0.5) # Position in top-left corner

        # Position the new label above the screen initially
        to_label.shift(UP * 2)

        # Add new circle and the off-screen label to the scene
        self.add(to_circle, to_label)

        # Define frame height threshold for dissolve (90% of frame height)
        FRAME_HEIGHT = self.camera.frame_height # Use camera attribute
        frame_height_threshold = FRAME_HEIGHT * 0.90 # Use 90%

        # Updater for first circle - fade out while shrinking
        def update_from_circle(circle):
            # Calculate progress
            progress = self.renderer.time / duration

            # Only fade out if we're past 40% of the animation
            if progress > 0.4:
                fade_progress = (progress - 0.4) / 0.2  # Fade out over 20% of animation
                circle.set_fill_opacity(max(0, 1.0 - fade_progress))
        # Updater for larger circle - fade in
        def update_to_circle(circle):
            # Calculate progress
            progress = self.renderer.time / duration

            # Only start to fade in when we're past the threshold
            if progress < 0.4:
                circle.set_opacity(0)
            elif progress < 0.6:
                fade_progress = (progress - 0.4) / 0.2  # Fade in over 20% of animation
                circle.set_opacity(fade_progress)
            else:
                circle.set_opacity(1.0)

            # Calculate circle size relative to frame
            circle_relative_size = circle.height / self.camera.frame_height  # Use camera attribute
            # Dissolve when circle exceeds threshold (90%)
            if circle_relative_size >= frame_height_threshold:
                # Calculate how far into dissolve we are (relative to the 90% threshold)
                exceeded_by = circle_relative_size - frame_height_threshold
                # Dissolve over a certain range (e.g., from 90% to 110% size)
                dissolve_range = 0.2  # Corresponds to 20% of frame height
                dissolve_progress = min(1.0, exceeded_by / dissolve_range)
                # Apply dissolve effect, but ensure opacity doesn't go below the fade-in progress
                current_opacity = circle.get_fill_opacity()
                dissolve_opacity = max(0, 1.0 - dissolve_progress)
                circle.set_fill_opacity(min(current_opacity, dissolve_opacity))

        # Create a ValueTracker for the scale
        scale_tracker = ValueTracker(from_scale)

        # Updater for scale indicator using the ValueTracker
        def update_scale(indicator):
            # Get the current scale from the tracker
            current_scale = scale_tracker.get_value()

            # Format scale using scientific notation
            scale_value_sci = f"{10**current_scale:.1e}"

            # Create new indicator with updated scale
            new_indicator = Text(
                f"{scale_value_sci} m",
                font="Arial",
                font_size=font_size,
                color=text_color
            ).to_corner(UR, buff=0.5)
            
            indicator.become(new_indicator)

        # Add updaters for circles and scale
        from_circle.add_updater(update_from_circle)
        to_circle.add_updater(update_to_circle)
        self.scale_indicator.add_updater(update_scale)

        # Calculate required scale factor for to_circle to reach target_radius
        target_scale_factor = target_radius / initial_to_radius

        # Set up the animations with new label animation
        self.play(
            from_circle.animate.scale(0.05),        # Shrink current circle dramatically (dissolves anyway)
            to_circle.animate.scale(target_scale_factor), # Shrink larger circle to target size
            from_label.animate.shift(LEFT * 4),     # Move old label left off-screen
            to_label.animate.shift(DOWN * 2),       # Move new label down into place
            scale_tracker.animate.set_value(to_scale), # Animate the scale value
            run_time=duration,
            rate_func=rate_functions.ease_in_out_sine
        )

        # Remove updaters
        from_circle.remove_updater(update_from_circle)
        to_circle.remove_updater(update_to_circle)
        self.scale_indicator.remove_updater(update_scale)

        # Clean up old circle and label objects
        self.remove(from_circle, from_label)

        # Update current objects
        self.current_circle = to_circle
        self.current_label = to_label

if __name__ == "__main__":
    # This script can be run directly with:
    # manim -pql updated_zoom.py ZoomAnimation
    # For higher quality:
    # manim -pqh updated_zoom.py ZoomAnimation
    pass
