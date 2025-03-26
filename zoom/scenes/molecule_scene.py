"""
Molecule scene implementation for NPQG Zoom Animation
Represents molecular structures at the 10^-8 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class MoleculeScene(ZoomableScene):
    """Scene representing molecular structures at 10^-8 m scale"""
    
    def __init__(self, config, scale_value=-8):
        """
        Initialize the molecule scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -8 (10^-8 m)
        """
        super().__init__(config, scale_value, "Molecule")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Molecule scene elements")
        elements = []
        
        try:
            # Create the main molecule boundary using the base class method
            # This will automatically load custom images if available
            molecule_radius = 3
            molecule_boundary = self.create_object(
                "Molecule",
                [0, 0, 0],
                molecule_radius
            )
            elements.append(molecule_boundary)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            # Check if we're using custom images and if an image was successfully loaded
            # The image is always the second element in the group if it exists
            has_custom_image = self.use_custom_images and len(molecule_boundary) > 2
                    
            if not self.use_custom_images or not has_custom_image:
                # Create a DNA molecule
                try:
                    dna = self._create_dna()
                    elements.append(dna)
                except Exception as e:
                    print(f"Error creating DNA: {e}")
                
                # Create a protein molecule
                try:
                    protein = self._create_protein()
                    elements.append(protein)
                except Exception as e:
                    print(f"Error creating protein: {e}")
                
                # Create water molecules
                try:
                    water = self._create_water_molecules()
                    elements.append(water)
                except Exception as e:
                    print(f"Error creating water molecules: {e}")
            
            print(f"Created {len(elements)} Molecule scene elements")
            return elements
        except Exception as e:
            print(f"Error in Molecule.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_dna(self):
        """Create a DNA double helix"""
        dna = VGroup()
        
        # Parameters for the helix
        height = 5.0  # Total height
        radius = 0.5  # Radius of the helix
        turns = 3.0   # Number of complete turns
        steps = 60    # Number of points to sample
        
        # Create the backbone curves
        backbone1_points = []
        backbone2_points = []
        
        for i in range(steps):
            t = i / (steps - 1)
            
            # Convert parameter to height and angle
            h = height * (t - 0.5)  # Center around origin
            angle = t * turns * TAU
            
            # First backbone coordinates with phase shift
            x1 = radius * np.cos(angle)
            y1 = radius * np.sin(angle)
            backbone1_points.append([x1, y1, h])
            
            # Second backbone coordinates (opposite side)
            x2 = radius * np.cos(angle + PI)
            y2 = radius * np.sin(angle + PI)
            backbone2_points.append([x2, y2, h])
        
        # Create backbone curves
        backbone1 = VMobject()
        backbone1.set_points_smoothly([np.array(p) for p in backbone1_points])
        backbone1.set_color(RED)
        backbone1.set_stroke(width=4)
        
        backbone2 = VMobject()
        backbone2.set_points_smoothly([np.array(p) for p in backbone2_points])
        backbone2.set_color(BLUE)
        backbone2.set_stroke(width=4)
        
        dna.add(backbone1, backbone2)
        
        # Add base pairs (rungs of the ladder)
        base_pairs = VGroup()
        
        for i in range(0, steps, 5):  # Add a base pair every 5 steps
            if i < steps - 1:
                # Get positions from the backbones
                pos1 = np.array(backbone1_points[i])
                pos2 = np.array(backbone2_points[i])
                
                # Create a line connecting the backbones
                base = Line(
                    start=pos1,
                    end=pos2,
                    stroke_color=GREEN,
                    stroke_width=2
                )
                
                base_pairs.add(base)
        
        dna.add(base_pairs)
        
        # Rotate to be vertical
        dna.rotate(PI/2, RIGHT)
        
        # Scale and position
        dna.scale(0.5)
        dna.shift(LEFT * 1.5)
        
        return dna
    
    def _create_protein(self):
        """Create a protein molecule (alpha helix)"""
        protein = VGroup()
        
        # Parameters for the alpha helix
        height = 4.0  # Total height
        radius = 0.4  # Radius of the helix
        turns = 5.0   # Number of complete turns
        steps = 50    # Number of points to sample
        
        # Create the backbone curve
        backbone_points = []
        
        for i in range(steps):
            t = i / (steps - 1)
            
            # Convert parameter to height and angle
            h = height * (t - 0.5)  # Center around origin
            angle = t * turns * TAU
            
            # Backbone coordinates
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            backbone_points.append([x, y, h])
        
        # Create backbone curve
        backbone = VMobject()
        backbone.set_points_smoothly([np.array(p) for p in backbone_points])
        backbone.set_color(YELLOW)
        backbone.set_stroke(width=5)
        
        protein.add(backbone)
        
        # Add amino acid residues
        residues = VGroup()
        
        for i in range(0, steps, 4):  # Add a residue every 4 steps
            if i < steps:
                # Get position from the backbone
                pos = np.array(backbone_points[i])
                
                # Calculate normal direction (perpendicular to the curve)
                normal = np.array([pos[0], pos[1], 0])
                normal = normal / np.linalg.norm(normal)
                
                # Position the residue along the normal
                residue_pos = pos + normal * 0.2
                
                # Create a sphere for the residue
                residue = Sphere(
                    radius=0.1,
                    fill_color=random.choice([RED, GREEN, BLUE, PURPLE, ORANGE]),
                    fill_opacity=0.8
                )
                residue.move_to(residue_pos)
                
                residues.add(residue)
        
        protein.add(residues)
        
        # Rotate to be vertical
        protein.rotate(PI/2, RIGHT)
        
        # Scale and position
        protein.scale(0.5)
        protein.shift(RIGHT * 1.5)
        
        return protein
    
    def _create_water_molecules(self):
        """Create scattered water molecules"""
        water_molecules = VGroup()
        
        # Number of water molecules
        num_molecules = 30
        
        for _ in range(num_molecules):
            # Random position within the scene
            r = np.random.uniform(0, 2.7)  # Keep within the scene circle
            theta = np.random.uniform(0, TAU)
            phi = np.random.uniform(0, PI)
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            # Create a water molecule (H2O)
            water = self._create_single_water_molecule()
            
            # Position the molecule
            water.move_to([x, y, z])
            
            # Random rotation
            water.rotate(np.random.uniform(0, TAU), RIGHT)
            water.rotate(np.random.uniform(0, TAU), UP)
            
            water_molecules.add(water)
        
        return water_molecules
    
    def _create_single_water_molecule(self):
        """Create a single water molecule"""
        water = VGroup()
        
        # Oxygen atom (larger, red)
        oxygen = Sphere(
            radius=0.1,
            fill_color="#FF0000",  # Red
            fill_opacity=0.8
        )
        
        # Hydrogen atoms (smaller, white)
        hydrogen1 = Sphere(
            radius=0.05,
            fill_color="#FFFFFF",  # White
            fill_opacity=0.8
        )
        hydrogen2 = Sphere(
            radius=0.05,
            fill_color="#FFFFFF",  # White
            fill_opacity=0.8
        )
        
        # Position hydrogen atoms
        angle = 104.5 * DEGREES  # H-O-H bond angle is approximately 104.5°
        bond_length = 0.2
        
        # Position hydrogens
        hydrogen1.move_to([bond_length * np.sin(angle/2), 0, bond_length * np.cos(angle/2)])
        hydrogen2.move_to([-bond_length * np.sin(angle/2), 0, bond_length * np.cos(angle/2)])
        
        # Create bonds
        bond1 = Line(
            start=oxygen.get_center(),
            end=hydrogen1.get_center(),
            stroke_color="#888888",
            stroke_width=2
        )
        
        bond2 = Line(
            start=oxygen.get_center(),
            end=hydrogen2.get_center(),
            stroke_color="#888888",
            stroke_width=2
        )
        
        water.add(oxygen, hydrogen1, hydrogen2, bond1, bond2)
        
        # Scale the whole molecule
        water.scale(0.3)
        
        return water