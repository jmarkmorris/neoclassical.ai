"""
Atom scene implementation for NPQG Zoom Animation
Represents atomic structures at the 10^-10 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class AtomScene(ZoomableScene):
    """Scene representing atomic structures at 10^-10 m scale"""
    
    def __init__(self, config, scale_value=-10):
        """
        Initialize the atom scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -10 (10^-10 m)
        """
        super().__init__(config, scale_value, "Atom")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Atom scene elements")
        elements = []
        
        try:
            # Create the main atom boundary using the base class method
            # This will automatically load custom images if available
            atom_radius = 3
            atom_boundary = self.create_object(
                "Atom",
                [0, 0, 0],
                atom_radius
            )
            elements.append(atom_boundary)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            has_custom_image = False
            for submob in atom_boundary.submobjects:
                if isinstance(submob, ImageMobject):
                    has_custom_image = True
                    break
                    
            if not self.use_custom_images or not has_custom_image:
                # Create the nucleus
                try:
                    nucleus = self._create_nucleus()
                    elements.append(nucleus)
                except Exception as e:
                    print(f"Error creating nucleus: {e}")
                
                # Create electron clouds/orbitals
                try:
                    electron_orbitals = self._create_electron_orbitals()
                    elements.append(electron_orbitals)
                except Exception as e:
                    print(f"Error creating electron orbitals: {e}")
                
                # Create electron particles
                try:
                    electrons = self._create_electrons()
                    elements.append(electrons)
                except Exception as e:
                    print(f"Error creating electrons: {e}")
            
            print(f"Created {len(elements)} Atom scene elements")
            return elements
        except Exception as e:
            print(f"Error in Atom.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_nucleus(self):
        """Create the atom's nucleus with protons and neutrons"""
        nucleus = VGroup()
        
        # Create a cluster of nucleons (protons and neutrons)
        num_nucleons = 16  # For an oxygen atom
        
        # Position nucleons in a packed spherical arrangement
        nucleons = VGroup()
        
        # Create a small sphere for each nucleon
        for i in range(num_nucleons):
            # Determine type - roughly equal numbers of protons and neutrons
            is_proton = (i % 2 == 0)
            
            # Position within a small central volume
            # Use spherical coordinates for even distribution
            if i == 0:
                # Center nucleon
                r = 0
                theta = 0
                phi = 0
            else:
                # Outer nucleons in a roughly spherical arrangement
                r = 0.15
                theta = np.random.uniform(0, TAU)
                phi = np.arccos(np.random.uniform(-1, 1))
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            # Slight jitter for packing appearance
            jitter = 0.03
            x += np.random.uniform(-jitter, jitter)
            y += np.random.uniform(-jitter, jitter)
            z += np.random.uniform(-jitter, jitter)
            
            # Create the nucleon
            if is_proton:
                color = "#FF4500"  # Red-orange for protons
            else:
                color = "#4682B4"  # Steel blue for neutrons
            
            nucleon = Sphere(
                radius=0.1,
                fill_color=color,
                fill_opacity=0.9
            )
            nucleon.move_to([x, y, z])
            
            nucleons.add(nucleon)
        
        # Add a glow around the nucleus to represent the strong force
        nuclear_force = Circle(
            radius=0.35,
            fill_color="#FFD700",  # Gold
            fill_opacity=0.2,
            stroke_width=0
        )
        
        nucleus.add(nuclear_force, nucleons)
        return nucleus
    
    def _create_electron_orbitals(self):
        """Create visualizations of electron orbitals"""
        orbitals = VGroup()
        
        # Create orbital shells (K, L)
        # K shell (1s)
        k_shell = Circle(
            radius=0.8,
            stroke_color="#1E90FF",  # Dodger blue
            stroke_width=2,
            stroke_opacity=0.6,
            fill_opacity=0
        )
        
        # L shell (2s, 2p)
        l_shell = Circle(
            radius=1.6,
            stroke_color="#1E90FF",
            stroke_width=2,
            stroke_opacity=0.4,
            fill_opacity=0
        )
        
        orbitals.add(k_shell, l_shell)
        
        # Create 2p orbitals (dumbbell shapes)
        p_orbitals = VGroup()
        
        # 2p orbital orientations (x, y, z)
        for i in range(3):
            # Choose orientation
            if i == 0:
                # 2px
                rotation_axis = UP
                rotation_angle = 0
            elif i == 1:
                # 2py
                rotation_axis = RIGHT
                rotation_angle = PI/2
            else:
                # 2pz
                rotation_axis = RIGHT
                rotation_angle = 0
            
            # Create a dumbbell shape for p orbital
            p_orbital = self._create_p_orbital()
            p_orbital.rotate(rotation_angle, rotation_axis)
            
            p_orbitals.add(p_orbital)
        
        orbitals.add(p_orbitals)
        
        # Add a subtle electron density cloud
        density_cloud = Circle(
            radius=2.0,
            fill_color="#ADD8E6",  # Light blue
            fill_opacity=0.1,
            stroke_width=0
        )
        
        orbitals.add(density_cloud)
        
        return orbitals
    
    def _create_p_orbital(self):
        """Create a p orbital dumbbell shape"""
        p_orbital = VGroup()
        
        # Distance from center
        distance = 1.6  # Match L shell radius
        
        # Create two lobes
        for sign in [-1, 1]:
            lobe = Sphere(
                radius=0.5,
                fill_color="#87CEFA",  # Light sky blue
                fill_opacity=0.3
            )
            lobe.move_to([0, 0, sign * distance])
            
            # Scale to create the dumbbell shape
            lobe.stretch(0.6, 0)
            lobe.stretch(0.6, 1)
            
            p_orbital.add(lobe)
        
        # Add a node at the center
        node = Sphere(
            radius=0.1,
            fill_color="#000000",
            fill_opacity=0.1
        )
        
        p_orbital.add(node)
        
        return p_orbital
    
    def _create_electrons(self):
        """Create electron particles orbiting the nucleus"""
        electrons = VGroup()
        
        # Number of electrons (8 for oxygen)
        num_electrons = 8
        
        # Create electrons on different shells
        # K shell: 2 electrons
        # L shell: 6 electrons
        
        # K shell electrons (1s orbital)
        for i in range(2):
            angle = i * PI  # Opposite sides
            
            radius = 0.8  # K shell radius
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create the electron
            electron = self._create_electron()
            electron.move_to([x, y, 0])
            
            electrons.add(electron)
        
        # L shell electrons (2s and 2p orbitals)
        for i in range(6):
            angle = i * TAU / 6  # Evenly spaced
            
            radius = 1.6  # L shell radius
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Add some z-variation for 3D effect
            z = 0.3 * np.sin(i * PI / 3)
            
            # Create the electron
            electron = self._create_electron()
            electron.move_to([x, y, z])
            
            electrons.add(electron)
        
        return electrons
    
    def _create_electron(self):
        """Create a single electron visualization"""
        electron = VGroup()
        
        # Core particle
        core = Dot(
            radius=0.08,
            color="#00FFFF",  # Cyan
            fill_opacity=0.9
        )
        
        # Quantum uncertainty visualization
        uncertainty = Circle(
            radius=0.15,
            stroke_color="#00FFFF",
            stroke_width=2,
            stroke_opacity=0.5,
            fill_color="#00FFFF",
            fill_opacity=0.2
        )
        
        electron.add(uncertainty, core)
        
        return electron