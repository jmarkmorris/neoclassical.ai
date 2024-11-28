# manim -pqh --disable_caching standard_model_3d.py standard_model_3d -p

# this is an example of multiple concurrent assemblies each defined by a dictionary.
# this code is sort of bulky. Possibly some cleverness related to the canonical model could make this code better.

# next step : animate the rotation of each animation.

from manim import *
import random
from numpy import array

run_time = 30
# run_time = 16
frame_rate = 30
# frame_rate = 60
# paused = False # add pause feature?

# powerpoint png export size
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate

radius_I = 0.1
radius_II = 0.2
radius_III = 0.3
radius_IV = 0.1
charge_radius = 0.05
personality_offset = .5

# debugging flags for looking at the part of the assembly
do_personality = 1
do_noether_core = 1
do_grid = 1

# interesting that t goes from 0 to 1, so run_time also plays a role in the speed of the animation.
# Let's go with frequency being the orbits per second of real time, i.e., Hz. 
# This is animation for ideation. In simulation there will be scale factors for every binary and personality charge, of course. 
# So we have: real_time = t * run_time
# And we know orbits = frequency * real_time. Therefore orbits = frequency * t * run_time
# Therefore our function needs to return this calculation. 
# This is a good rate function to reuse in other animations. 
# To Do : create a library and add this to it.
def frequency(f):
    def func(t):
        return (f * t * run_time) % 1
        # return min(t * f, 1)
    return func

class standard_model_3d(ThreeDScene):
    def construct(self):
        # In Manim, phi and theta are parameters that define the orientation of the camera in a 3D scene. 
        # phi is the polar angle, which is the angle between the Z-axis and the camera through the origin, measured in radians
        # theta is the azimuthal angle, which is the angle that spins the camera around the Z-axis.

        # in this animation, z is coming out of the screen. x is the assembly type, and y is the generation.
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.camera.background_color = BLACK        

        text = Paragraph(
                    '  Title : Standard Model Fermion Architecture Hypothesis.'
                    '  Author : J Mark Morris.'
                    '  Mapping : Standard model generation (I, II, III) + Noether core binaries (III, II, I) = 4.\n'
                    '  Insight : Assemblies flatten with velocity.'
                    '  Mapping : Color charge may correspond to the three geometries for each quark.'
                    '  Mapping : Electron and neutrino have no color charge due to symmetry.\n'
                    '  Mapping : High energy reactions can cause decay of outer Noether core binaries.'
                    '  Mapping : Outer binary decay makes apparent energy (e.g., mass) previously shielded by superposition.\n'
                    '  Mapping : Quark orbital plane orientations logically match Weinberg angle (~tau/12). (not shown)'
                    '  Note : The other charge distribution geometry possibilities for quarks and neutrinos seem counterintuitive.\n'
                    '  Mapping : Orbital poles of Noether core binaries precess with spin "1/2" (i.e., f/2). (not shown)'
                    '  Insight : The architecture is a nested nucleus model.'
                    '  Insight : The ontology is consistent with reductionism.\n'
                    '  Mapping : Each Noether core contains shielded energy consistent with the Gen II and Gen III fermions.'
                    '  The shielded nature of the Noether core assembly may map to dark matter and dark energy.\n'
                    '  Note : Salient characteristics of each binary are orders of magnitude different (i.e.,  velocity, radius, and energy) '
                    '  Note : Animations are abstract. The diagrams are not to scale. Radii of binaries TBD.\n',
                    font="Helvetica Neue", 
                    font_size=20, 
                    weight=ULTRALIGHT, 
                    line_spacing=0.5)
        text.scale(0.5)
        text.to_corner(UL)
        text.shift(LEFT*0.25 + UP*0.25)
        self.add_fixed_in_frame_mobjects(text)

        starting_x = -6.0
        x_increment = 1.7
        y_decrement = 2.25
        dictionary_of_assemblies = []
        for x in range(8):  
            starting_y = 1.5
            for y in range(3):
                assembly = {
                    'position': (starting_x, starting_y, 0),
                }
                dictionary_of_assemblies.append(assembly)
                
                starting_y -= y_decrement
            starting_x += x_increment

        assembly_labels = ["Electron", "Muon", "Tau", 
                           "Down A","Strange A","Bottom A", 
                           "Down B","Strange B","Bottom B", 
                           "Down C","Strange C","Bottom C", 
                           "Electron Neutrino", "Muon Neutrino", "Tau Neutrino", 
                           "Up A","Charm A","Top A", 
                           "Up B","Charm B","Top B", 
                           "Up C","Charm C","Top C",
                           ]
        
        # Best practice for initializing repetitive dictionary items
        for i, A in enumerate(dictionary_of_assemblies):
            A['font'] = "Helvetica Neue"
            A['font_size'] = 12
            A['weight'] = MEDIUM
            A['color'] = WHITE
            A['text']  = assembly_labels[i]
   
        charges_in_the_noether_core = [
            {
                'center': (radius_I,0,0),
                'color': PURE_RED,
                'dot_radius': charge_radius,
                'orbit_radius': radius_I,
                'frequency': 4,
                'orbit_rotate': 0,
                'path_rotate':[0, 0, 1],
                'orbit_normal':[0, 0, 1]
            },
            {
                'center': (-radius_I,0,0),
                'color': PURE_BLUE,
                'dot_radius': charge_radius,
                'orbit_radius': radius_I,
                'frequency': 4,
                'orbit_rotate': 0,
                'path_rotate':[0, 0, 1],
                'orbit_normal':[0, 0, 1]
            },
            {
                'center': (0,radius_II,0),
                'color': PURE_RED,
                'dot_radius': charge_radius,
                'orbit_radius': radius_II,
                'frequency': 3,
                'orbit_rotate': PI/2,
                'path_rotate':[0, 1, 0],
                'orbit_normal':[1, 0, 0]
            },
            {
                'center': (0,-radius_II,0),
                'color': PURE_BLUE,
                'dot_radius': charge_radius,
                'orbit_radius': radius_II,
                'frequency': 3,
                'orbit_rotate': PI/2,
                'path_rotate':[0, 1, 0],
                'orbit_normal':[1, 0, 0]
            },
            {
                'center': (0,0,radius_III),
                'color': PURE_RED,
                'dot_radius': charge_radius,
                'orbit_radius': radius_III,
                'frequency': 2,
                'orbit_rotate': PI/2,
                'path_rotate':[1, 0, 0],
                'orbit_normal':[0, 1, 0]
            },
            {
                'center': (0,0,-radius_III),
                'color': PURE_BLUE,
                'dot_radius': charge_radius,
                'orbit_radius': radius_III,
                'frequency': 2,
                'orbit_rotate': PI/2,
                'path_rotate':[1, 0, 0],
                'orbit_normal':[0, 1, 0]
            }
        ]

        personality_charges = [
            {
                'center': (personality_offset, radius_IV, 0),
                'dot_radius': charge_radius,
                'orbit_origin': (personality_offset, 0, 0),
                'orbit_normal': [1, 0, 0]
            },
            {
                'center': (-personality_offset, radius_IV, 0),
                'dot_radius': charge_radius,
                'orbit_origin': (personality_offset, 0, 0),
                'orbit_normal': [1, 0, 0]
            },
            {
                'center': (0, personality_offset, radius_IV),
                'dot_radius': charge_radius,
                'orbit_origin': (0, personality_offset, 0),
                'orbit_normal': [0, 1, 0]
            },
            {
                'center': (0, -personality_offset, radius_IV),
                'dot_radius': charge_radius,
                'orbit_origin': (0, personality_offset, 0),
                'orbit_normal': [0, 1, 0]
            },
            {
                'center': (radius_IV, 0, personality_offset),
                'dot_radius': charge_radius,
                'orbit_origin': (0, 0, personality_offset),
                'orbit_normal': [0, 0, 1]
            },
            {
                'center': (radius_IV, 0, -personality_offset),
                'dot_radius': charge_radius,
                'orbit_origin': (0, 0, personality_offset),
                'orbit_normal': [0, 0, 1]
            }
        ]

        assemblies = []
        for i, A in enumerate(dictionary_of_assemblies):
            
            '''
            set up the text label for each assembly.
            '''
            T = Text(
                A['text'],
                font=A['font'],
                font_size=A['font_size'],
                weight=A['weight'],
                color=A['color']
            ).move_to(A['position']+array([0,1,0]))
            # self.add(T)
            self.add_fixed_in_frame_mobjects(T)

            '''
            set up the 3D coordinate axes for each assembly.
            '''
            if do_grid:
                kwargs = {
                    'x_range': [-5,5,1],
                    'y_range': [-5,5,1],
                    'z_range': [-5,5,1],
                    'x_length': 1.5,
                    'y_length': 1.5,
                    'z_length': 1.5,
                    'tips': False,
                    'axis_config': {
                        'stroke_width':1,
                        'include_ticks': False,
                    },
                }
                axes = ThreeDAxes(**kwargs)
                # x_axis_label = axes.get_x_axis_label(label="x")
                # x_axis_label.size = 12
                # self.add(x_axis_label)
                # y_axis_label = axes.get_y_axis_label(label="y")
                # self.add(y_axis_label)
                # z_axis_label = axes.get_z_axis_label(label="z")
                # z_axis_label.rotate(PI)
                # self.add(z_axis_label)
                # this code needs to put the axes and the label into an animation group
                axes.move_to(A['position'])
                self.add(axes)

            '''
            animate the noether core.
            '''
            if do_noether_core:
                for c, charge in enumerate(charges_in_the_noether_core):
                    
                    assembly = A['text']
                    if assembly in ["Electron", "Down A", "Down B", "Down C", "Electron Neutrino", "Up A", "Up B", "Up C"]:
                        generation = 3
                    elif assembly in ["Muon", "Strange A", "Strange B", "Strange C", "Muon Neutrino", "Charm A", "Charm B", "Charm C"]:
                        generation = 2
                    elif assembly in ["Tau", "Bottom A", "Bottom B", "Bottom C", "Tau Neutrino", "Top A", "Top B", "Top C"]:
                        generation = 1
                    
                    if ((c in [2, 3]) and generation == 1) or ((c in [4, 5]) and (generation in [1, 2])):
                        continue

                    kwargs = {
                        'point':charge['center'], 
                        'radius':charge['dot_radius'], 
                        'color':charge['color'],
                    }
                    sphere = Dot3D(**kwargs)
                    
                    kwargs = {
                        'radius':charge['orbit_radius'],
                        'color':WHITE,
                        'stroke_opacity':0.5,
                        'stroke_width':1,
                        'fill_opacity':0.0,
                    }
                    if (c % 2) == 0: kwargs['stroke_opacity'] = 0 # this one is not shown and the odd one is.
                    orbital_path = Circle(**kwargs)
                    if (c % 2) == 0: orbital_path.rotate_about_origin(PI) # this moves the start of the circle path
                    orbital_path.move_to(A['position'])
                    orbital_path.rotate(angle=charge['orbit_rotate'], axis=charge['path_rotate'])
                    self.add(orbital_path, sphere)

                    orbits = []
                    for _ in range(charge['frequency']):
                        orbit = MoveAlongPath(sphere, 
                                            orbital_path, 
                                            # radians=TAU, 
                                            rate_func=frequency(charge['frequency']), 
                                            run_time=run_time
                                            )
                        orbits.append(orbit)
                    
                    assemblies.append(AnimationGroup(*orbits))
                    # lag_ratio=1 didn't solve it
                

            '''
            animate the personality charges.
            '''
            if do_personality:
                assembly = A['text']
         
                for p, personality in enumerate(personality_charges):
                    # personality orbital path
                    i = p // 2
                    j = personality_offset
                    if p % 2:
                        j = -j
                    kwargs = {
                        'radius':radius_IV,
                        'color':WHITE,
                        'stroke_opacity':0.5,
                        'stroke_width':1,
                        'fill_opacity':0.0,
                    }
                    personality_orbital_path = Circle(**kwargs)
                    position = [0, 0, 0]
                    position[i] = j
                    personality_orbital_path.move_to(array(position)+array(A['position']))
                    if i == 0:
                        personality_orbital_path.rotate(PI/2, axis=Y_AXIS)
                    elif i == 1:
                        personality_orbital_path.rotate(PI/2, axis=X_AXIS)
                    self.add(personality_orbital_path)

                    color = PURE_BLUE #start every charge at blue here and change selected ones to red
                    if assembly in ["Electron", "Muon", "Tau"]:
                        color = PURE_BLUE
                    elif assembly in ["Down A", "Strange A", "Bottom A"]:
                        if p in [3, 5]:
                            color = PURE_RED
                    elif assembly in ["Down B", "Strange B", "Bottom B"]:
                        if p in [1, 5]:
                            color = PURE_RED
                    elif assembly in ["Down C", "Strange C", "Bottom C"]:
                        if p in [1, 3]:
                            color = PURE_RED
                    elif assembly in ["Electron Neutrino", "Muon Neutrino", "Tau Neutrino"]:
                        if p in [1, 3, 5]:
                            color = PURE_RED
                    elif assembly in ["Up A", "Charm A", "Top A"]:
                        if p in [1, 2, 3, 4, 5]:
                            color = PURE_RED
                    elif assembly in ["Up B", "Charm B", "Top B"]:
                        if p in [0, 1, 3, 4, 5]:
                            color = PURE_RED
                    elif assembly in ["Up C", "Charm C", "Top C"]:
                        if p in [0, 1, 2, 3, 4]:
                            color = PURE_RED     

                    kwargs = {
                        'point':personality['center'],
                        'color':color,
                        'radius':personality['dot_radius'],
                    }
                    dot = Dot3D(**kwargs)
                    dot.shift(A['position'])
                    self.add(dot)
                    assemblies.append(MoveAlongPath(dot, 
                                                    personality_orbital_path, 
                                                    radians=TAU*32, 
                                                    rate_func=frequency(1), 
                                                    run_time=run_time
                                                    ))
                
        self.play(*assemblies) 

        self.wait(0)

