# # manim noether.py noether -pqm --disable_caching -p
#  rm /Users/markmorris/Documents/NPQG_Code_Base/NPQG/manim/media/videos/noether/1686p30/noether.mp4; manim noether.py noether -pqh --disable_caching -p

# this could be implemented more generally with the fermion.py and skipping over the personality charges with an if statement.
# however, for now I am going to fork them because may want to do different things with the base noether core model.
# they could be merged back at some point.

from manim import *
import random
# import json

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
run_time = 30
# run_time = 60
# run_time = 16
frame_rate = 30
# frame_rate = 60
# paused = False # add pause feature?

print_text = False

# powerpoint png export size
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate

radius_I = 0.25
radius_II = 1.25
radius_III = 2.5
# radius_IV = 0.3
# personality_offset = 2.85



class noether(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
        self.camera.background_color = INDIGO
   
        charges = [
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
                'orbit_cycles': 32,
                'orbit_rotate': PI/2,
                'path_rotate':[0, 1, 0],
                'orbit_normal':[1, 0, 0]
            },
            {
                'center': (0,-radius_II,0),
                'color': PURE_BLUE,
                'orbit_radius': radius_II,
                'orbit_cycles': 32,
                'orbit_rotate': PI/2,
                'path_rotate':[0, 1, 0],
                'orbit_normal':[1, 0, 0]
            },
            {
                'center': (0,0,radius_III),
                'color': PURE_RED,
                'orbit_radius': radius_III,
                'orbit_cycles': 8,
                'orbit_rotate': PI/2,
                'path_rotate':[1, 0, 0],
                'orbit_normal':[0, 1, 0]
            },
            {
                'center': (0,0,-radius_III),
                'color': PURE_BLUE,
                'orbit_radius': radius_III,
                'orbit_cycles': 8,
                'orbit_rotate': PI/2,
                'path_rotate':[1, 0, 0],
                'orbit_normal':[0, 1, 0]
            }
        ]

        # personalities = [
        #     {
        #         'center': (personality_offset, radius_IV, 0),
        #         'color': PURE_BLUE,
        #         'orbit_origin': (personality_offset, 0, 0),
        #         'orbit_normal': [1, 0, 0]
        #     },
        #     {
        #         'center': (-personality_offset, radius_IV, 0),
        #         'color': PURE_BLUE,
        #         'orbit_origin': (personality_offset, 0, 0),
        #         'orbit_normal': [1, 0, 0]
        #     },
        #     {
        #         'center': (0, personality_offset, radius_IV),
        #         'color': PURE_BLUE,
        #         'orbit_origin': (0, personality_offset, 0),
        #         'orbit_normal': [0, 1, 0]
        #     },
        #     {
        #         'center': (0, -personality_offset, radius_IV),
        #         'color': PURE_BLUE,
        #         'orbit_origin': (0, personality_offset, 0),
        #         'orbit_normal': [0, 1, 0]
        #     },
        #     {
        #         'center': (radius_IV, 0, personality_offset),
        #         'color': PURE_BLUE,
        #         'orbit_origin': (0, 0, personality_offset),
        #         'orbit_normal': [0, 0, 1]
        #     },
        #     {
        #         'center': (radius_IV, 0, -personality_offset),
        #         'color': PURE_BLUE,
        #         'orbit_origin': (0, 0, personality_offset),
        #         'orbit_normal': [0, 0, 1]
        #     }
        # ]

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
        for charge in charges:
            orbital_path = Circle(radius=charge['orbit_radius'], color=WHITE, stroke_opacity=0.5, stroke_width=1)
            orbital_path.rotate(angle=charge['orbit_rotate'], axis=charge['path_rotate'])
            self.add(orbital_path)

            sphere = Dot3D(point=charge['center'])
            sphere.set_color(charge['color'])
            self.add(sphere)

            animations.append(Rotating(sphere, radians=TAU*charge['orbit_cycles'], axis=charge['orbit_normal'], about_point=ORIGIN, rate_func=linear, run_time=run_time))
        
        # for personality in personalities:
        #     dot = Dot3D(point=personality['center'], color=personality['color'])
        #     self.add(dot)
        #     animations.append(Rotating(dot, radians=TAU*32, axis=personality['orbit_normal'], about_point=personality['orbit_origin'], rate_func=linear, run_time=run_time))
        
        # for i in range(3):
        #     for j in [-personality_offset, personality_offset]:
        #         personality_orbital_path = Circle(radius=radius_IV, color=WHITE, stroke_opacity=0.5, stroke_width=1, fill_color=WHITE, fill_opacity=0.3)
        #         position = [0, 0, 0]
        #         position[i] = j
        #         personality_orbital_path.move_to(position)
        #         if i == 0:
        #             personality_orbital_path.rotate(PI/2, axis=Y_AXIS)
        #         elif i == 1:
        #             personality_orbital_path.rotate(PI/2, axis=X_AXIS)
        #         self.add(personality_orbital_path)

        # if (print_text):
        #     text = Text('Fermion Architecture Hypothesis        by J Mark Morris\nMoving architrinos cause changing electromagnetic fields.\nOrbiting charges form strong electromagnetic fields in each axial vortex.\nAxial potential fields map to the strong force.\nThe orbital axes precess with spin 1/2 (not shown).\nEach orbiting dipole has an angular momentum vector.\nThe angular momentum vectors have magnitudes S,M,L.\nThere are two distinct orderings: SML and SLM, which map to pro and anti.\nEither ordering can spin left or right.\nThe central nest of three orbiting dipoles is a Noether core.', font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
        #     text.to_corner(UL)
        #     text.shift(LEFT*0.25 + UP*0.25)
        #     self.add_fixed_in_frame_mobjects(text)

        #     text = Text('Personality charges (- or +) are bound in each vortex.\nPersonality charges map to the weak force.\nNoether core orbital plane orientation is influenced by personality charges.\nColor charge maps to personality charge S,M,L dipole configuration.\nThe architecture has many symmetries.\nCharges continuously emit spherical potential streams.\nPath histories determine potential sphere streams and action.\nThe Noether core contracts and becomes more oblate as group velocity rises.\nGroup velocity facilitates change from Fermi-Dirac to Bose-Einstein statistics.', font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
        #     text.to_corner(DL)
        #     text.shift(LEFT*0.25 + DOWN*0.25)
        #     self.add_fixed_in_frame_mobjects(text)

        #     text = Text('The Noether core sub-assembly is reused in all bosons.\nPhotons are contra-rotating planar Noether cores.\nHiggs are Noether cores with near perfect shielding by superposition.\nW and Z bosons are ephemeral transitionary configurations.\narchitrinos are indestructable. No beginning. No end.\narchitrinos have provenance and may be tracked in reactions.\nIn this animation, the camera rotates around the fermion assembly.', font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
        #     text.to_corner(UR)
        #     text.shift(RIGHT*0.25 + UP*0.25)
        #     self.add_fixed_in_frame_mobjects(text)

        #     text = Text("architrinos have no fundamental speed limit.\nAssemblies may impose an emergent speed limit.\nOrbiting charges with v = field speed are the symmetry breaking point.\nThe smallest orbital radius and maximum curvature maps to Planck scale.\nThe orbital radii are at vastly different scales.\nDipoles broker energy in quanta of angular momentum.\nNoether cores are stretchy rulers and variable clocks. (ala Einstein's GR)", font="Helvetica Neue", font_size=12, weight=ULTRALIGHT, line_spacing=0.5)
        #     text.to_corner(DR)
        #     text.shift(RIGHT*0.25 + DOWN*0.25)
        #     self.add_fixed_in_frame_mobjects(text)

        self.begin_ambient_camera_rotation(rate=TAU/16)
        self.play(*animations)
        self.stop_ambient_camera_rotation()

        self.wait(0)




