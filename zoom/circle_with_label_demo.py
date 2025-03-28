#\!/usr/bin/env python3
"""
Demo script to show circles with labels on the right side
that dissolve when they reach 95% of the frame height
"""

from manim import *
import numpy as np

# Set background color
INDIGO = "#4B0082"

class CircleWithLabelDemo(Scene):
    def construct(self):
        # Set the background color
        self.camera.background_color = INDIGO
        
        # Get frame dimensions from config
        FRAME_WIDTH = config.frame_width
        FRAME_HEIGHT = config.frame_height
        
        # Create a background object
        background = Rectangle(
            width=FRAME_WIDTH * 2,
            height=FRAME_HEIGHT * 2,
            fill_color=INDIGO,
            fill_opacity=1,
            stroke_width=0,
            z_index=-10
        )
        self.add(background)
        
        # Create first circle with label
        circle1 = Circle(
            radius=1,
            stroke_color=WHITE,
            fill_color="#3366CC",
            fill_opacity=0.8,
            z_index=1
        )
        
        # Position label to the right of the circle
        label1 = Text(
            "Universe",
            font="Arial",
            font_size=36,
            color=WHITE
        ).next_to(circle1, RIGHT, buff=0.5)
        
        # Create second (initially tiny) circle with label
        circle2 = Circle(
            radius=0.01,  # Start very small
            stroke_color=WHITE,
            fill_color="#CC3366", # Different color
            fill_opacity=0.8,
            z_index=1
        )
        
        # Create label for second circle (initially invisible)
        label2 = Text(
            "Galaxy Cluster",
            font="Arial",
            font_size=36,
            color=WHITE
        ).next_to(circle2, RIGHT, buff=0.5)
        label2.scale(0.01)  # Scale down with the circle
        label2.set_opacity(0)  # Start invisible
        
        # Add all elements to the scene
        self.add(circle1, label1, circle2, label2)
        
        # Define frame height threshold (95% of frame height)
        frame_height_threshold = FRAME_HEIGHT * 0.95
        dissolve_duration = 2.0  # 2 second dissolve effect
        
        # Add updaters to make label follow circle during zoom
        def update_label1(label):
            label.next_to(circle1, RIGHT, buff=0.5)
            # Calculate circle size relative to frame
            circle_relative_size = circle1.height / FRAME_HEIGHT
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                label.set_opacity(1.0 - dissolve_progress)
        
        def update_label2(label):
            label.next_to(circle2, RIGHT, buff=0.5)
            # Match the circle's scale to keep sizes proportional
            # Only need to update opacity (scale updated by animation)
            progress = self.renderer.time / 3.0  # Total animation duration
            if progress < 0.4:
                label.set_opacity(0)
            elif progress < 0.6:
                fade_progress = (progress - 0.4) / 0.2
                label.set_opacity(fade_progress)
            else:
                label.set_opacity(1.0)
        
        # Add updaters for circle1's dissolve effect
        def update_circle1(circle):
            # Calculate circle size relative to frame
            circle_relative_size = circle.height / FRAME_HEIGHT
            # Dissolve when circle exceeds threshold
            if circle_relative_size >= 0.95:
                # Calculate how far into dissolve we are
                exceeded_by = circle_relative_size - 0.95
                dissolve_progress = min(1.0, exceeded_by / 0.2)  # Dissolve over next 20% growth
                circle.set_opacity(1.0 - dissolve_progress)
        
        # Add the updaters
        label1.add_updater(update_label1)
        label2.add_updater(update_label2)
        circle1.add_updater(update_circle1)
        
        # Create continuous animation
        self.play(
            circle1.animate.scale(20),  # Zoom first circle to be very large
            circle2.animate.scale(100), # Grow second circle to visible size
            run_time=3,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # Remove updaters
        label1.remove_updater(update_label1)
        label2.remove_updater(update_label2)
        circle1.remove_updater(update_circle1)
        
        # Pause at the end
        self.wait(1)

if __name__ == "__main__":
    # This script can be run directly with:
    # manim -pql circle_with_label_demo.py CircleWithLabelDemo
    pass
