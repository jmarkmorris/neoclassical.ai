# Ensure that you are running in a virtual environment (venv).  cd to NPQG and look at venv.READE.me
# manim fermion.py fermion -pqm --disable_caching -p

from manim import *
import random
# import json

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
run_time = 30
# run_time = 16
frame_rate = 60
# frame_rate = 60
# paused = False # add pause feature?

print_text = True

# powerpoint png export size
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate

radius_I = 0.25
radius_II = 0.5
radius_III = 0.8
radius_IV = 0.3
personality_offset = 2.85

# Initialize the dictionary with all parts set to False
parts_to_animate = {i: False for i in range(1, 7)}
# 1 : binary I
# 2 : binary II
# 3 : binary III
# 4 : personalities for binary I
# 5 : personalities for binary II
# 6 : personalities for binary III

# To animate all parts
for part in parts_to_animate:
    parts_to_animate[part] = True

# To animate parts 2, 5, and 6
# for part in [2, 5, 6]:
#     parts_to_animate[part] = True
    
# Initialize the personality colors with all parts set to PURE_BLUE
personality_colors = {i: PURE_BLUE for i in range(1, 7)}
for personality in [3,4,5,6]:
    personality_colors[personality] = PURE_RED

class fermion(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
        self.camera.background_color = INDIGO
   
        potentials = [
            {
                'center': (radius_I,0,0),
                'color': PURE_RED,
                'orbit_radius': radius_I,
                'orbit_cycles': 128,
                'orbit_rotate': 0,
                'path_rotate':[0, 0, 1],
                'orbit_normal':[0, 0, 1]
            },
            {
                'center': (-radius_I,0,0),
                'color': PURE_BLUE,
                'orbit_radius': radius_I,
                'orbit_cycles': 128,
                'orbit_rotate': 0,
                'path_rotate':[0, 0, 1],
                'orbit_normal':[0, 0, 1]
            },
            {
                'center': (0,radius_II,0),
                'color': PURE_RED,
                'orbit_radius': radius_II,
                'orbit_cycles': 64,
                'orbit_rotate': PI/2,
                'path_rotate':[0, 1, 0],
                'orbit_normal':[1, 0, 0]
            },
            {
                'center': (0,-radius_II,0),
                'color': PURE_BLUE,
                'orbit_radius': radius_II,
                'orbit_cycles': 64,
                'orbit_rotate': PI/2,
                'path_rotate':[0, 1, 0],
                'orbit_normal':[1, 0, 0]
            },
            {
                'center': (0,0,radius_III),
                'color': PURE_RED,
                'orbit_radius': radius_III,
                'orbit_cycles': 32,
                'orbit_rotate': PI/2,
                'path_rotate':[1, 0, 0],
                'orbit_normal':[0, 1, 0]
            },
            {
                'center': (0,0,-radius_III),
                'color': PURE_BLUE,
                'orbit_radius': radius_III,
                'orbit_cycles': 32,
                'orbit_rotate': PI/2,
                'path_rotate':[1, 0, 0],
                'orbit_normal':[0, 1, 0]
            }
        ]

        personalities = [
            {
                'center': (personality_offset, radius_IV, 0),
                'color': personality_colors[1],
                'orbit_origin': (personality_offset, 0, 0),
                'orbit_normal': [1, 0, 0]
            },
            {
                'center': (-personality_offset, radius_IV, 0),
                'color': personality_colors[2],
                'orbit_origin': (personality_offset, 0, 0),
                'orbit_normal': [1, 0, 0]
            },
            {
                'center': (0, personality_offset, radius_IV),
                'color': personality_colors[3],
                'orbit_origin': (0, personality_offset, 0),
                'orbit_normal': [0, 1, 0]
            },
            {
                'center': (0, -personality_offset, radius_IV),
                'color': personality_colors[4],
                'orbit_origin': (0, personality_offset, 0),
                'orbit_normal': [0, 1, 0]
            },
            {
                'center': (radius_IV, 0, personality_offset),
                'color': personality_colors[5],
                'orbit_origin': (0, 0, personality_offset),
                'orbit_normal': [0, 0, 1]
            },
            {
                'center': (radius_IV, 0, -personality_offset),
                'color': personality_colors[6],
                'orbit_origin': (0, 0, personality_offset),
                'orbit_normal': [0, 0, 1]
            }
        ]

        kwargs = {
            'x_range': [-5,5,1],
            'y_range': [-5,5,1],
            'z_range': [-5,5,1],
            'x_length': 7,
            'y_length': 7,
            'z_length': 7,
            'axis_config': {
                'tip_shape': ArrowTriangleTip
            }
        }
        axes = ThreeDAxes(**kwargs)
        x_axis_label = axes.get_x_axis_label(label="x")
        self.add(x_axis_label)
        y_axis_label = axes.get_y_axis_label(label="y")
        self.add(y_axis_label)
        z_axis_label = axes.get_z_axis_label(label="z")
        z_axis_label.rotate(PI)
        self.add(z_axis_label)
        self.add(axes)

        animations = []
        for potential in potentials:
            orbital_path = Circle(radius=potential['orbit_radius'], color=WHITE, stroke_opacity=0.5, stroke_width=1)
            orbital_path.rotate(angle=potential['orbit_rotate'], axis=potential['path_rotate'])
            self.add(orbital_path)

            sphere = Dot3D(point=potential['center'])
            sphere.set_color(potential['color'])
            self.add(sphere)

            animations.append(Rotating(sphere, radians=TAU*potential['orbit_cycles'], axis=potential['orbit_normal'], about_point=ORIGIN, rate_func=linear, run_time=run_time))
        
        for personality in personalities:
            dot = Dot3D(point=personality['center'], color=personality['color'])
            self.add(dot)
            animations.append(Rotating(dot, radians=TAU*32, axis=personality['orbit_normal'], about_point=personality['orbit_origin'], rate_func=linear, run_time=run_time))
        
        for i in range(3):
            for j in [-personality_offset, personality_offset]:
                personality_orbital_path = Circle(radius=radius_IV, color=WHITE, stroke_opacity=0.5, stroke_width=1, fill_color=WHITE, fill_opacity=0.3)
                position = [0, 0, 0]
                position[i] = j
                personality_orbital_path.move_to(position)
                if i == 0:
                    personality_orbital_path.rotate(PI/2, axis=Y_AXIS)
                elif i == 1:
                    personality_orbital_path.rotate(PI/2, axis=X_AXIS)
                self.add(personality_orbital_path)

        if (print_text):
            text = Text(
'''
Fermion Architecture Hypothesis       by J Mark Morris
The architecture is a story of emergent symmetries of a dynamical path geometry.
The background is Euclidean 3D space and linear forward moving time.
The background is populated with energy carrying neoclassical point potentials.
Point potentials are constant rate potential emitters with |q|=|e|/6.
Point potentials are potential receivers with paths influenced by action.
Point potentials are indestructible. No origin story. No ending story.
Point potentials have provenance and may be traced in reactions.
Point potentials are modeled as a Dirac delta at r=0 with a magnitude q/|v|,
evolving to a potential sphere expanding at r=@t with magnitude q/|v|r.
Path histories determine potential sphere streams, superposition, and action.
A single evolution equation at t=now evolves the path of all point potentials.
Point potentials have no fundamental speed limit.
Assemblies may impose an emergent speed limit.
''', 
            font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
            text.to_corner(UL)
            text.shift(LEFT*0.25 + UP*0.25)
            self.add_fixed_in_frame_mobjects(text)

            text = Text(
'''
A point potential binary forms spiral potential fields and polar vortices.
Axial vortex potential fields map to the strong force.
A binary with: 
    v < field speed (@) is in the expansion/contraction regime (CFT:partner action)
    v = field speed is at the symmetry breaking point (Planck scale).
    v > field speed is in the inflation/deflation regime (AdS:partner+self action).
The smallest orbital radius and maximum curvature maps to meridional v = @pi/2.
Binaries broker energy in quanta of angular momentum.
Fermion personality potentials (- or +) may bind in an axial vortex.
Fermion personality point potentials map to the weak force.
''',
            font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
            text.to_corner(DL)
            text.shift(LEFT*0.25 + DOWN*0.25)
            self.add_fixed_in_frame_mobjects(text)
            
            text = Text(
'''
The nuclei is a triply nested set of orbiting binaries, a Noether core.
The Noether core sub-assembly is reused in all fermions and bosons.
Photons are contra-rotating planar Noether cores.
Gravitons are high energy Noether cores with near perfect shielding
due to a combination of q/v emissions and superposition.
Gravitons are created in SMBH and emit/jet through the event horizon.
W and Z bosons are ephemeral transitionary configurations.
Noether core orbital plane orientation is influenced by personality potentials.
Each orbiting binary in a Noether core has an angular momentum vector.
The angular momentum vectors have magnitudes Small, Medium, Large.
There are two distinct orderings: SML and SLM, which map to pro and anti.
''',
            font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
            text.to_corner(UR)
            text.shift(RIGHT*0.25 + UP*0.25)
            self.add_fixed_in_frame_mobjects(text)
            
            

            text = Text(
'''
The radius & frequency of Noether core binaries have vastly different scales.
Noether cores implement stretchy rulers and variable clocks. (ala GR)
Increasing group velocity or intense gravity change the Noether core geometry: 
    scales by contraction/deflation 
    becomes more oblate and/or distorts.
    changes from Fermi-Dirac (3D) and Bose-Einstein (2D) statistics.
The orbital axes precess with spin 1/2 in a fermion (not shown).
Either precession ordering can spin left or right.
Color charge results from mapping personality potentials to S,M,L binaries.
''',
            font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
            text.to_corner(DR)
            text.shift(RIGHT*0.25 + DOWN*0.25)
            self.add_fixed_in_frame_mobjects(text)

        self.begin_ambient_camera_rotation(rate=TAU/16)
        self.play(*animations)
        self.stop_ambient_camera_rotation()

        self.wait(0)




