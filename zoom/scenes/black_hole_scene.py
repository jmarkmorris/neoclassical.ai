"""
Black Hole scene implementation for NPQG Zoom Animation
Represents a supermassive black hole at the 10^12 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class BlackHoleScene(ZoomableScene):
    """Scene representing a supermassive black hole at 10^12 m scale"""
    
    def __init__(self, config, scale_value=12):
        """
        Initialize the black hole scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 12 (10^12 m)
        """
        super().__init__(config, scale_value, "Black Hole")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Black Hole scene elements")
        elements = []
        
        try:
            # Create the main black hole region using the base class method
            # This will automatically load custom images if available
            bh_radius = 3
            bh_region = self.create_object(
                "Black Hole",
                [0, 0, 0],
                bh_radius
            )
            elements.append(bh_region)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            has_custom_image = False
            for submob in bh_region.submobjects:
                if isinstance(submob, ImageMobject):
                    has_custom_image = True
                    break
                    
            if not self.use_custom_images or not has_custom_image:
                # Create the black hole event horizon
                try:
                    event_horizon = self._create_event_horizon()
                    elements.append(event_horizon)
                except Exception as e:
                    print(f"Error creating event horizon: {e}")
                
                # Create the accretion disk
                try:
                    accretion_disk = self._create_accretion_disk()
                    elements.append(accretion_disk)
                except Exception as e:
                    print(f"Error creating accretion disk: {e}")
                
                # Create relativistic jets
                try:
                    jets = self._create_jets()
                    elements.append(jets)
                except Exception as e:
                    print(f"Error creating jets: {e}")
                
                # Create the gravitational lensing effect
                try:
                    lensing = self._create_gravitational_lensing()
                    elements.append(lensing)
                except Exception as e:
                    print(f"Error creating gravitational lensing: {e}")
            
            print(f"Created {len(elements)} Black Hole scene elements")
            return elements
        except Exception as e:
            print(f"Error in BlackHole.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_event_horizon(self):
        """Create the black hole's event horizon"""
        # Event horizon is a completely black circle
        horizon = Circle(
            radius=0.6,
            fill_color="#000000",
            fill_opacity=1.0,
            stroke_width=1,
            stroke_color="#333333"
        )
        
        # Add a subtle glow around the horizon
        glow = Circle(
            radius=0.65,
            fill_opacity=0,
            stroke_width=5,
            stroke_color="#4B0082",  # Indigo
            stroke_opacity=0.3
        )
        
        return VGroup(horizon, glow)
    
    def _create_accretion_disk(self):
        """Create the black hole's accretion disk"""
        # Create the accretion disk as a series of rings with gradient colors
        disk = VGroup()
        
        # Inner radius just outside event horizon
        inner_radius = 0.65
        # Outer radius of the disk
        outer_radius = 2.5
        # Number of rings to create
        num_rings = 50
        
        for i in range(num_rings):
            # Calculate this ring's radius
            t = i / (num_rings - 1)
            radius = inner_radius + t * (outer_radius - inner_radius)
            
            # Calculate thickness (thicker near center)
            thickness = 0.08 * (1 - 0.7 * t)
            
            # Calculate color (transition from blue-white to orange-red)
            if t < 0.5:
                # Inner disk: blue to white (hotter)
                color = interpolate_color("#1E90FF", "#FFFFFF", t * 2)
                opacity = 0.9 - 0.4 * t
            else:
                # Outer disk: white to orange to red (cooler)
                outer_t = (t - 0.5) * 2
                color = interpolate_color("#FFFFFF", "#FF4500", outer_t)
                opacity = 0.5 - 0.3 * outer_t
            
            # Create a ring with no fill, just a colored stroke
            ring = Circle(
                radius=radius,
                fill_opacity=0,
                stroke_width=thickness * 100,  # Multiply by 100 to make it visible
                stroke_color=color,
                stroke_opacity=opacity
            )
            
            # Add some rotation to make it elliptical
            ring.stretch(0.4, 1)  # Stretch vertically
            ring.rotate(PI/4)  # Rotate to show perspective
            
            disk.add(ring)
        
        # Add some particles in the disk for texture
        particles = VGroup()
        for _ in range(100):
            # Random position in polar coordinates
            r = np.random.uniform(inner_radius * 1.1, outer_radius * 0.95)
            theta = np.random.uniform(0, TAU)
            
            # Adjust radius to fit the elliptical shape
            adjusted_r = r * (0.4 + 0.6 * abs(np.cos(theta)))
            
            # Convert to Cartesian
            x = adjusted_r * np.cos(theta)
            y = adjusted_r * np.sin(theta) * 0.4  # Apply the stretch
            
            # Rotate to match disk orientation
            x_rot = x * np.cos(PI/4) - y * np.sin(PI/4)
            y_rot = x * np.sin(PI/4) + y * np.cos(PI/4)
            
            # Determine color and size based on distance
            if r < (inner_radius + outer_radius) / 3:
                color = "#FFFFFF"  # White for inner disk
                size = np.random.uniform(0.01, 0.03)
                opacity = np.random.uniform(0.7, 1.0)
            elif r < 2 * (inner_radius + outer_radius) / 3:
                color = "#FFD700"  # Gold for middle disk
                size = np.random.uniform(0.01, 0.025)
                opacity = np.random.uniform(0.5, 0.8)
            else:
                color = "#FF4500"  # Red-orange for outer disk
                size = np.random.uniform(0.005, 0.02)
                opacity = np.random.uniform(0.3, 0.6)
            
            particle = Dot(
                point=[x_rot, y_rot, 0],
                radius=size,
                color=color,
                fill_opacity=opacity
            )
            particles.add(particle)
        
        return VGroup(disk, particles)
    
    def _create_jets(self):
        """Create relativistic jets perpendicular to the disk"""
        # Create two oppositely directed jets
        jets = VGroup()
        
        # Jet parameters
        jet_length = 1.8
        jet_width = 0.3
        jet_angle = PI/4  # Match the accretion disk rotation
        
        # Create jets using a series of cones with opacity gradient
        for direction in [-1, 1]:  # Top and bottom jets
            jet = VGroup()
            
            # Number of segments for each jet
            num_segments = 20
            
            for i in range(num_segments):
                # Calculate position along the jet
                t = i / (num_segments - 1)
                
                # Jet becomes narrower and less opaque as it extends
                width_factor = 1 - 0.7 * t
                opacity = 0.7 - 0.6 * t
                
                # Calculate the segment dimensions
                segment_length = jet_length / num_segments
                segment_width = jet_width * width_factor
                
                # Base is at the black hole
                base_center = np.array([0, 0, 0])
                # Tip is extended outward
                jet_direction = np.array([np.sin(jet_angle), direction * np.cos(jet_angle), 0])
                tip_center = base_center + jet_direction * (t * jet_length)
                
                # Create a small conical segment
                segment = Triangle(
                    fill_color="#4B0082",  # Indigo for jets
                    fill_opacity=opacity,
                    stroke_width=0
                )
                segment.scale(segment_width)
                
                # Position the segment along the jet
                segment.move_to(tip_center)
                # Rotate to point in the jet direction
                angle = np.arctan2(jet_direction[1], jet_direction[0])
                segment.rotate(angle + PI/2 * direction)
                
                jet.add(segment)
            
            jets.add(jet)
        
        # Add some particle effects in the jets
        particles = VGroup()
        for _ in range(40):
            # Choose a jet (top or bottom)
            direction = np.random.choice([-1, 1])
            
            # Random position along the jet
            t = np.random.random()
            jet_direction = np.array([np.sin(jet_angle), direction * np.cos(jet_angle), 0])
            
            # Add some spread perpendicular to jet direction
            perp_direction = np.array([jet_direction[1], -jet_direction[0], 0])
            spread = np.random.normal(0, 0.1) * perp_direction
            
            # Calculate position
            pos = t * jet_length * jet_direction + spread
            
            # Create a particle
            particle = Dot(
                point=pos,
                radius=np.random.uniform(0.01, 0.03),
                color="#9370DB",  # Light purple
                fill_opacity=np.random.uniform(0.3, 0.8)
            )
            particles.add(particle)
        
        jets.add(particles)
        return jets
    
    def _create_gravitational_lensing(self):
        """Create a visualization of gravitational lensing"""
        # Create a group for all lensing effects
        lensing = VGroup()
        
        # Create background stars that appear distorted
        num_stars = 50
        for _ in range(num_stars):
            # Random position in the background (away from the center)
            distance = np.random.uniform(1.0, 2.8)
            angle = np.random.uniform(0, TAU)
            
            # Calculate undistorted position
            x_undistorted = distance * np.cos(angle)
            y_undistorted = distance * np.sin(angle)
            
            # Calculate the lensing effect (more pronounced closer to the center)
            # This uses a simplified model of gravitational lensing
            distortion_factor = 0.8 / (distance + 0.4)  # Stronger effect near the center
            
            # Apply distortion: stars appear to bend around the black hole
            # The distortion is tangential to the radial direction
            tangent_angle = angle + PI/2
            
            # Calculate the distortion offset
            distortion_x = distortion_factor * np.cos(tangent_angle)
            distortion_y = distortion_factor * np.sin(tangent_angle)
            
            # Apply the distortion
            x_distorted = x_undistorted + distortion_x
            y_distorted = y_undistorted + distortion_y
            
            # Create a streak instead of a dot to show lensing
            if distance < 1.5:  # Stronger effect for closer stars
                # Create an arc to represent the lensed image
                # Calculate the arc center and radius
                arc_angle = np.arctan2(y_undistorted, x_undistorted)
                arc_radius = np.sqrt(x_undistorted**2 + y_undistorted**2)
                
                # Create the arc
                arc_length = TAU * 0.1 * (1.5 - distance) / 1.5  # Longer arcs closer to the black hole
                arc = Arc(
                    radius=arc_radius,
                    angle=arc_length,
                    color="#FFFFFF",
                    stroke_width=2,
                    stroke_opacity=0.8 - 0.4 * distance / 1.5
                )
                
                # Position the arc
                arc.rotate(arc_angle - arc_length/2)
                
                lensing.add(arc)
            else:
                # For more distant stars, just create a slightly elongated dot
                star = Dot(
                    point=[x_distorted, y_distorted, 0],
                    radius=np.random.uniform(0.01, 0.02),
                    color="#FFFFFF",
                    fill_opacity=np.random.uniform(0.4, 0.7)
                )
                
                # Slightly stretch the dot in the tangential direction
                star.stretch(1 + distortion_factor*2, 0)
                star.rotate(tangent_angle)
                
                lensing.add(star)
        
        return lensing