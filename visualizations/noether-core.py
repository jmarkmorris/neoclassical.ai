
## manim noether_core.py noether_core -pqh --disable_caching -p



from manim import *

'''
The idea is to animate the 3D path of architrinos in a Noether core as the orbitals precess.

What we are animating here doesn't seem to match the definition of Lissajous figure which are 2D, and which trace the coordinate
given by two oscillations in different spatial dimensions.


A Lissajous curve, also known as a Lissajous figure or Bowditch curve, is the graph of a system of parametric equations that describe 
the superposition of two perpendicular oscillations in the x and y directions of different angular frequencies (a and b). 
These curves were first studied by Nathaniel Bowditch in 1815 and later in more detail by Jules Antoine Lissajous in 1857.

The appearance of the figure is sensitive to the ratio of a/b. 
For a ratio of 1, when the frequencies match (a=b), the figure is an ellipse, with special cases including circles and lines. 
A small change to one of the frequencies will mean the x oscillation after one cycle will be slightly out of synchronization 
with the y motion and so the ellipse will fail to close and trace a curve slightly adjacent during the next orbit showing as 
a precession of the ellipse. The pattern closes if the frequencies are whole number ratios i.e. a/b is rational.

To Do
- add tracers so we can see that actual path
- build up a Noether core

'''

class lissajou(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK
        self.set_camera_orientation(phi=70 * DEGREES, theta=45 * DEGREES)

        kwargs = {
            'x_range': [-5,5,1],
            'y_range': [-5,5,1],
            'z_range': [-5,5,1],
            'x_length': 6,
            'y_length': 6,
            'z_length': 6,
            'tips': False,
            'axis_config': {
                'stroke_width':1,
                'include_ticks': False,
            },
        }
        axes = ThreeDAxes(**kwargs)
        self.add(axes)

        orbital_path1 = Circle(radius=1, stroke_color=WHITE, stroke_width = 1, stroke_opacity = 1)
        orbital_path2 = Circle(radius=1, stroke_color=RED, stroke_opacity=0)
        orbital_path2.rotate_about_origin(PI)
        orbital_path3 = Circle(radius=2, stroke_color=WHITE, stroke_width = 1, stroke_opacity = 1)
        orbital_path4 = Circle(radius=2, stroke_color=RED, stroke_opacity=0)
        orbital_path4.rotate_about_origin(PI)
        orbital_path5 = Circle(radius=3, stroke_color=WHITE, stroke_width = 1, stroke_opacity = 1)
        orbital_path6 = Circle(radius=3, stroke_color=RED, stroke_opacity=0)
        orbital_path6.rotate_about_origin(PI)
        self.add(orbital_path1) 
        self.add(orbital_path2) 
        self.add(orbital_path3) 
        self.add(orbital_path4) 
        self.add(orbital_path5) 
        self.add(orbital_path6) 

        sphere1 = Dot3D(radius=0.1, color=PURE_RED, fill_opacity=1)
        sphere2 = Dot3D(radius=0.1, color=PURE_BLUE, fill_opacity=1)
        sphere3 = Dot3D(radius=0.1, color=PURE_RED, fill_opacity=1)
        sphere4 = Dot3D(radius=0.1, color=PURE_BLUE, fill_opacity=1)
        sphere5 = Dot3D(radius=0.1, color=PURE_RED, fill_opacity=1)
        sphere6 = Dot3D(radius=0.1, color=PURE_BLUE, fill_opacity=1)
        self.add(sphere1) 
        self.add(sphere2) 
        self.add(sphere3) 
        self.add(sphere4) 
        self.add(sphere5) 
        self.add(sphere6) 

        
        self.play(
            MoveAlongPath(sphere1, orbital_path1),
            MoveAlongPath(sphere2, orbital_path2),
            MoveAlongPath(sphere3, orbital_path3),
            MoveAlongPath(sphere4, orbital_path4),
            MoveAlongPath(sphere5, orbital_path5),
            MoveAlongPath(sphere6, orbital_path6),
            Rotate(orbital_path1, angle=PI, axis=IN),
            Rotate(orbital_path2, angle=PI, axis=IN),
            Rotate(orbital_path3, angle=PI, axis=LEFT),
            Rotate(orbital_path4, angle=PI, axis=LEFT),
            Rotate(orbital_path5, angle=PI, axis=UP),
            Rotate(orbital_path6, angle=PI, axis=UP),
            run_time=10,
            rate_func=linear
        )

