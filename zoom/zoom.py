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

# Set background color
INDIGO = "#4B0082"

class ZoomAnimation(Scene):
    def construct(self):
        # Load config
        config_path = "zoom_config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Set the background color - just like in the demo
        self.camera.background_color = INDIGO
        
        # Get frame dimensions from config - just like in the demo
        FRAME_WIDTH = config.frame_width
        FRAME_HEIGHT = config.frame_height
        
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
            
            # Calculate duration based on scale difference
            scale_diff = abs(to_scale - from_scale)
            secs_per_decade = self.config["global_settings"].get("scale_seconds_per_decade", 3.0)
            min_duration = self.config["global_settings"].get("min_transition_duration", 4.0)
            max_duration = self.config["global_settings"].get("max_transition_duration", 15.0)
            
            duration = scale_diff * secs_per_decade
            duration = max(min_duration, min(max_duration, duration))
            
            # Override if explicitly provided
            if "duration" in transition:
                duration = transition["duration"]
            
            print(f"Animating {direction} from {from_scene} (10^{int(round(from_scale))}) to {to_scene} (10^{int(round(to_scale))}), Duration: {duration}")
            
            if i == 0:
                # For the first transition, initialize the scene
                self._setup_scene(from_scene, from_scale, to_scene, to_scale)
            
            # Perform the zoom animation using demo-like approach
            if direction == "in":
                self._zoom_in(from_scene, to_scene, from_scale, to_scale, duration)
            else:
                self._zoom_out(from_scene, to_scene, from_scale, to_scale, duration)
            
            # Add a small pause between transitions for clarity
            if i < len(animation_sequence) - 1:
                self.wait(0.5)
    
    def _setup_scene(self, from_scene, from_scale, to_scene, to_scale):
        """Set up the initial scene with first circle and scale indicator"""
        # Set the background color
        self.camera.background_color = INDIGO
        
        # Get frame dimensions from config
        FRAME_WIDTH = config.frame_width
        FRAME_HEIGHT = config.frame_height
        
        # Create background - similar to the demo
        bg_color = self.config["global_settings"].get("background_color", INDIGO)
        background = Rectangle(
            width=FRAME_WIDTH * 2,
            height=FRAME_HEIGHT * 2,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0,
            z_index=-10
        )
        self.add(background)
        
        # Create the initial circle using the demo's approach
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
        
        self.current_circle = Circle(
            radius=1,  # Start with the same radius as demo
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
        ).next_to(self.current_circle, RIGHT, buff=0.5)
        
        # Create scale indicator with integer value only
        scale_text = f"10^{int(round(from_scale))}"
        self.scale_indicator = Text(
            f"{scale_text} m",
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
        to_circle = Circle(
            radius=0.01,  # Start very small like in demo
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
        ).next_to(to_circle, RIGHT, buff=0.5)
        
        # Scale down to match circle but keep proportions
        to_label.scale(0.01)  # Scale down with the circle
        to_label.set_opacity(0)  # Start invisible but will fade in
        
        # Add new elements to scene
        self.add(to_circle, to_label)
        
        # Define frame height threshold for dissolve (95% of frame height)
        FRAME_HEIGHT = config.frame_height
        frame_height_threshold = FRAME_HEIGHT * 0.95
        
        # Updater for first circle - dissolve when too large
        def update_from_circle(circle):
            # Calculate circle size relative to frame
            circle_relative_size = circle.height / FRAME_HEIGHT
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                circle.set_opacity(max(0, 1.0 - dissolve_progress))
        
        # Updater for first label - follow circle and dissolve
        def update_from_label(label):
            label.next_to(from_circle, RIGHT, buff=0.5)
            # Calculate circle size relative to frame
            circle_relative_size = from_circle.height / FRAME_HEIGHT
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                label.set_opacity(max(0, 1.0 - dissolve_progress))
        
        # Updater for second label - directly tied to circle size
        def update_to_label(label):
            # Make sure the label stays with its circle
            label.next_to(to_circle, RIGHT, buff=0.5)
            # Determine visibility based on size - progressively increase
            size_factor = to_circle.width / config.frame_width
            if size_factor > 0.05:  # Only show when circle is big enough
                label.set_opacity(min(1.0, size_factor * 10))
            else:
                label.set_opacity(0)
        
        # Updater for scale indicator with integer values only
        def update_scale(indicator):
            progress = self.renderer.time / duration
            
            # Calculate current scale value (linear interpolation)
            current_scale = from_scale + (to_scale - from_scale) * progress
            
            # Always use integer scale factors as requested
            scale_text = f"10^{int(round(current_scale))}"
            
            # Create new indicator with updated scale
            new_indicator = Text(
                f"{scale_text} m",
                font="Arial",
                font_size=font_size,
                color=text_color
            ).to_corner(UR, buff=0.5)
            
            indicator.become(new_indicator)
        
        # Add the updaters
        from_label.add_updater(update_from_label)
        to_label.add_updater(update_to_label)
        from_circle.add_updater(update_from_circle)
        self.scale_indicator.add_updater(update_scale)
        
        # Create continuous animation - with larger scale
        self.play(
            from_circle.animate.scale(20),        # Zoom first circle to be very large
            to_circle.animate.scale(200),         # Grow second circle to visible size (much larger scale)
            run_time=duration,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Remove updaters
        from_label.remove_updater(update_from_label)
        to_label.remove_updater(update_to_label)
        from_circle.remove_updater(update_from_circle)
        self.scale_indicator.remove_updater(update_scale)
        
        # Clean up old objects
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
        
        # Create the larger circle that we're zooming out to
        to_circle = Circle(
            radius=5,  # Start at medium size
            stroke_color=WHITE,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )
        
        # Set initial state
        to_circle.scale(4.0)  # Make it larger than from_circle
        to_circle.set_opacity(0)  # Start invisible
        
        # Create the label for the larger circle with high z-index
        to_label = Text(
            to_scene,
            font="Arial",
            font_size=font_size,
            color=text_color,
            z_index=5  # Very high z-index to ensure it stays on top
        ).next_to(to_circle, RIGHT, buff=0.5)
        
        # Start with to_label invisible
        to_label.set_opacity(0)
        
        # Add new elements to scene
        self.add(to_circle, to_label)
        
        # Define frame height threshold for dissolve (95% of frame height)
        FRAME_HEIGHT = config.frame_height
        frame_height_threshold = FRAME_HEIGHT * 0.95
        
        # Updater for first circle - fade out while shrinking
        def update_from_circle(circle):
            # Calculate progress
            progress = self.renderer.time / duration
            
            # Only fade out if we're past 40% of the animation
            if progress > 0.4:
                fade_progress = (progress - 0.4) / 0.2  # Fade out over 20% of animation
                circle.set_opacity(max(0, 1.0 - fade_progress))
        
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
            circle_relative_size = circle.height / FRAME_HEIGHT
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                circle.set_opacity(max(0, 1.0 - dissolve_progress))
        
        # Updater for first label - follow circle and fade out
        def update_from_label(label):
            # Keep label next to circle
            label.next_to(from_circle, RIGHT, buff=0.5)
            
            # Keep in sync with the opacity of its circle
            label.set_opacity(from_circle.get_fill_opacity())
        
        # Updater for second label - follow circle and fade in
        def update_to_label(label):
            # Keep label next to circle
            label.next_to(to_circle, RIGHT, buff=0.5)
            
            # Keep in sync with the opacity of its circle
            label.set_opacity(to_circle.get_fill_opacity())
        
        # Updater for scale indicator with integer values only
        def update_scale(indicator):
            progress = self.renderer.time / duration
            
            # Calculate current scale value (linear interpolation)
            current_scale = from_scale + (to_scale - from_scale) * progress
            
            # Always use integer scale factors as requested
            scale_text = f"10^{int(round(current_scale))}"
            
            # Create new indicator with updated scale
            new_indicator = Text(
                f"{scale_text} m",
                font="Arial",
                font_size=font_size,
                color=text_color
            ).to_corner(UR, buff=0.5)
            
            indicator.become(new_indicator)
        
        # Add updaters
        from_circle.add_updater(update_from_circle)
        from_label.add_updater(update_from_label)
        to_circle.add_updater(update_to_circle)
        to_label.add_updater(update_to_label)
        self.scale_indicator.add_updater(update_scale)
        
        # Set up the animations
        self.play(
            from_circle.animate.scale(0.05),  # Shrink current circle dramatically
            to_circle.animate.scale(0.2),     # Adjust larger circle size
            run_time=duration,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Remove updaters
        from_circle.remove_updater(update_from_circle)
        from_label.remove_updater(update_from_label)
        to_circle.remove_updater(update_to_circle)
        to_label.remove_updater(update_to_label)
        self.scale_indicator.remove_updater(update_scale)
        
        # Clean up old objects
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