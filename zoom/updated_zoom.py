#\!/usr/bin/env python3
"""
Improved NPQG Universe Zoom Animation
- Labels positioned next to circles
- Labels zoom with circles
- Circles and labels dissolve at 95% of frame height
- Continuous zooming without pauses
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
        
        # Set the background color
        self.camera.background_color = INDIGO
        
        # Get frame dimensions
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
            
            print(f"Animating {direction} from {from_scene} (10^{from_scale}) to {to_scene} (10^{to_scale}), Duration: {duration}")
            
            if i == 0:
                # For the first transition, initialize the scene
                self._setup_scene(from_scene, from_scale, to_scene, to_scale)
            
            # Perform the zoom animation
            if direction == "in":
                self._zoom_in(from_scene, to_scene, from_scale, to_scale, duration)
            else:
                self._zoom_out(from_scene, to_scene, from_scale, to_scale, duration)
    
    def _setup_scene(self, from_scene, from_scale, to_scene, to_scale):
        """Set up the initial scene with first circle and scale indicator"""
        # Create background
        bg_color = self.config["global_settings"].get("background_color", "#4B0082")
        background = Rectangle(
            width=config.frame_width * 4,
            height=config.frame_height * 4,
            fill_color=bg_color,
            fill_opacity=1.0,
            stroke_width=0,
            z_index=-10
        )
        self.add(background)
        
        # Create the initial circle
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
        
        self.current_circle = Circle(
            radius=3,
            stroke_color=WHITE,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )
        
        # Create label for the circle
        font_size = self.config["global_settings"].get("font_size", 36)
        text_color = self.config["global_settings"].get("color_text", "#FFFFFF")
        
        self.current_label = Text(
            from_scene,
            font="Arial",
            font_size=font_size,
            color=text_color
        ).next_to(self.current_circle, RIGHT, buff=0.5)
        
        # Create scale indicator
        self.scale_indicator = Text(
            f"10^{from_scale} m",
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
        
        # Create the next (smaller) circle
        to_circle = Circle(
            radius=3,
            stroke_color=WHITE,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )
        
        # Start tiny and invisible
        initial_scale_ratio = 0.01
        to_circle.scale(initial_scale_ratio)
        to_circle.set_opacity(0)  # Start invisible
        to_circle.move_to(ORIGIN)
        
        # Create the next label
        to_label = Text(
            to_scene,
            font="Arial",
            font_size=font_size,
            color=text_color
        ).next_to(to_circle, RIGHT, buff=0.5)
        
        # Scale and hide the to_label
        to_label.scale(initial_scale_ratio)
        to_label.set_opacity(0)
        
        # Add new elements to scene
        self.add(to_circle, to_label)
        
        # Set up the animations
        self.play(
            from_circle.animate.scale(100),  # Zoom out current circle dramatically
            to_circle.animate.scale(1/initial_scale_ratio),  # Grow second circle to normal size
            run_time=duration,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Updater for first circle - dissolve when too large
        def update_from_circle(circle, dt):
            # Calculate circle size relative to frame
            circle_relative_size = circle.height / config.frame_height
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                circle.set_opacity(max(0, 1.0 - dissolve_progress))
            
            # Also handle crossfade based on animation progress
            progress = self.renderer.time / duration
            if 0.3 <= progress <= 0.7:
                fade_progress = (progress - 0.3) / 0.4
                # Only apply if not already dissolving due to size
                if circle_relative_size < 0.95:
                    circle.set_opacity(max(0, 1.0 - fade_progress))
        
        # Updater for second circle - fade in during transition
        def update_to_circle(circle, dt):
            progress = self.renderer.time / duration
            if progress < 0.3:
                circle.set_opacity(0)
            elif progress < 0.7:
                fade_progress = (progress - 0.3) / 0.4
                circle.set_opacity(fade_progress)
            else:
                circle.set_opacity(1.0)
        
        # Updater for first label - follow circle and dissolve
        def update_from_label(label, dt):
            # Keep label next to circle
            label.next_to(from_circle, RIGHT, buff=0.5)
            
            # Calculate circle size relative to frame
            circle_relative_size = from_circle.height / config.frame_height
            
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                label.set_opacity(max(0, 1.0 - dissolve_progress))
            
            # Also handle crossfade based on animation progress
            progress = self.renderer.time / duration
            if 0.3 <= progress <= 0.7:
                fade_progress = (progress - 0.3) / 0.4
                # Only apply if not already dissolving due to size
                if circle_relative_size < 0.95:
                    label.set_opacity(max(0, 1.0 - fade_progress))
        
        # Updater for second label - follow circle and fade in
        def update_to_label(label, dt):
            # Keep label next to circle
            label.next_to(to_circle, RIGHT, buff=0.5)
            
            # Handle opacity based on animation progress
            progress = self.renderer.time / duration
            if progress < 0.3:
                label.set_opacity(0)
            elif progress < 0.7:
                fade_progress = (progress - 0.3) / 0.4
                label.set_opacity(fade_progress)
            else:
                label.set_opacity(1.0)
        
        # Updater for scale indicator
        def update_scale(indicator, dt):
            progress = self.renderer.time / duration
            
            # Calculate current scale value (linear interpolation)
            current_scale = from_scale + (to_scale - from_scale) * progress
            
            # Create new indicator with updated scale
            new_indicator = Text(
                f"10^{current_scale:.1f} m",
                font="Arial",
                font_size=font_size,
                color=text_color
            ).to_corner(UR, buff=0.5)
            
            indicator.become(new_indicator)
        
        # Add updaters
        from_circle.add_updater(update_from_circle)
        to_circle.add_updater(update_to_circle)
        from_label.add_updater(update_from_label)
        to_label.add_updater(update_to_label)
        self.scale_indicator.add_updater(update_scale)
        
        # Wait a tiny amount to let the updaters work
        self.wait(0.01)
        
        # Remove updaters
        from_circle.remove_updater(update_from_circle)
        to_circle.remove_updater(update_to_circle)
        from_label.remove_updater(update_from_label)
        to_label.remove_updater(update_to_label)
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
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
        
        # Store current elements
        from_circle = self.current_circle
        from_label = self.current_label
        
        # Create the larger circle that we're zooming out to
        to_circle = Circle(
            radius=3,
            stroke_color=WHITE,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1
        )
        
        # Start very large and invisible
        initial_scale_ratio = 100
        to_circle.scale(initial_scale_ratio)
        to_circle.set_opacity(0)
        to_circle.move_to(ORIGIN)
        
        # Create the label for the larger circle
        to_label = Text(
            to_scene,
            font="Arial",
            font_size=font_size,
            color=text_color
        ).next_to(to_circle, RIGHT, buff=0.5)
        
        # Start with to_label invisible
        to_label.set_opacity(0)
        
        # Add new elements to scene
        self.add(to_circle, to_label)
        
        # Set up the animations
        self.play(
            from_circle.animate.scale(0.01),  # Shrink current circle dramatically
            to_circle.animate.scale(1/initial_scale_ratio),  # Shrink large circle to normal size
            run_time=duration,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Updater for first circle - fade out
        def update_from_circle(circle, dt):
            progress = self.renderer.time / duration
            if progress < 0.3:
                circle.set_opacity(1.0)
            elif progress < 0.7:
                fade_progress = (progress - 0.3) / 0.4
                circle.set_opacity(1.0 - fade_progress)
            else:
                circle.set_opacity(0.0)
        
        # Updater for second circle - fade in
        def update_to_circle(circle, dt):
            progress = self.renderer.time / duration
            if progress < 0.3:
                circle.set_opacity(0)
            elif progress < 0.7:
                fade_progress = (progress - 0.3) / 0.4
                circle.set_opacity(fade_progress)
            else:
                circle.set_opacity(1.0)
        
        # Updater for first label - follow circle and fade out
        def update_from_label(label, dt):
            # Keep label next to circle
            label.next_to(from_circle, RIGHT, buff=0.5)
            
            # Handle opacity based on animation progress
            progress = self.renderer.time / duration
            if progress < 0.3:
                label.set_opacity(1.0)
            elif progress < 0.7:
                fade_progress = (progress - 0.3) / 0.4
                label.set_opacity(1.0 - fade_progress)
            else:
                label.set_opacity(0.0)
        
        # Updater for second label - follow circle and fade in
        def update_to_label(label, dt):
            # Keep label next to circle
            label.next_to(to_circle, RIGHT, buff=0.5)
            
            # Handle opacity based on animation progress
            progress = self.renderer.time / duration
            if progress < 0.3:
                label.set_opacity(0)
            elif progress < 0.7:
                fade_progress = (progress - 0.3) / 0.4
                label.set_opacity(fade_progress)
            else:
                label.set_opacity(1.0)
        
        # Updater for scale indicator
        def update_scale(indicator, dt):
            progress = self.renderer.time / duration
            
            # Calculate current scale value (linear interpolation)
            current_scale = from_scale + (to_scale - from_scale) * progress
            
            # Create new indicator with updated scale
            new_indicator = Text(
                f"10^{current_scale:.1f} m",
                font="Arial",
                font_size=font_size,
                color=text_color
            ).to_corner(UR, buff=0.5)
            
            indicator.become(new_indicator)
        
        # Add updaters
        from_circle.add_updater(update_from_circle)
        to_circle.add_updater(update_to_circle)
        from_label.add_updater(update_from_label)
        to_label.add_updater(update_to_label)
        self.scale_indicator.add_updater(update_scale)
        
        # Wait a tiny amount to let the updaters work
        self.wait(0.01)
        
        # Remove updaters
        from_circle.remove_updater(update_from_circle)
        to_circle.remove_updater(update_to_circle)
        from_label.remove_updater(update_from_label)
        to_label.remove_updater(update_to_label)
        self.scale_indicator.remove_updater(update_scale)
        
        # Clean up old objects
        self.remove(from_circle, from_label)
        
        # Update current objects
        self.current_circle = to_circle
        self.current_label = to_label

if __name__ == "__main__":
    # Process command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Run NPQG Universe Zoom Animation")
    parser.add_argument("--config", help="Path to JSON configuration file", default="zoom_config.json")
    parser.add_argument("--quality", choices=["l", "m", "h"], default="m", help="Quality preset (l=low, m=medium, h=high)")
    parser.add_argument("--output", default="zoom_animation.mp4", help="Output file name")
    
    args, unknown_args = parser.parse_known_args()
    
    # Run the scene
    quality_flag = f"-q{args.quality}"
    os.system(f"manim {quality_flag} -p updated_zoom.py ZoomAnimation")
