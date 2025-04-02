# manim -pqk --disable_caching Lorenz3D.py Lorenz3D -p

from manim import *
import numpy as np
from tools import INDIGO, ELECTRIC_PURPLE

class Lorenz3D(ThreeDScene):
    """
    Visualization of the Lorenz attractor in 3D space
    """
    def construct(self):
        # Set up the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.camera.frame_center = ORIGIN
        
        # Parameters for the Lorenz system
        sigma = 10
        beta = 8/3
        rho = 28
        
        # Function to compute the Lorenz derivatives
        def lorenz_deriv(xyz, t0, sigma=sigma, beta=beta, rho=rho):
            x, y, z = xyz
            return [
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ]
        
        # Create axes
        axes = ThreeDAxes(
            x_range=[-30, 30, 5],
            y_range=[-30, 30, 5],
            z_range=[0, 60, 10],
            x_length=6,
            y_length=6,
            z_length=6,
            axis_config={"include_tip": True, "include_ticks": True}
        )
        
        # Add axes labels
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        z_label = axes.get_z_axis_label("z", edge=OUT, direction=OUT)
        
        # Add title
        title = Text("Lorenz Attractor", font_size=36)
        title.to_corner(UL)
        
        # Add the axes and labels to the scene
        self.add(axes, x_label, y_label, z_label, title)
        
        # Create the Lorenz attractor curve
        dt = 0.01
        num_steps = 10000
        
        # Initial conditions
        xyz = np.array([0.1, 0.0, 0.0])
        
        # Create the curve
        curve = VMobject(stroke_width=2, stroke_color=ELECTRIC_PURPLE)
        points = [axes.coords_to_point(*xyz)]
        
        # Compute the trajectory
        for i in range(num_steps):
            # Use Euler method to update the position
            dxyz = lorenz_deriv(xyz, 0)
            xyz = xyz + np.array(dxyz) * dt
            points.append(axes.coords_to_point(*xyz))
        
        # Set the points of the curve
        curve.set_points_smoothly(points)
        
        # Create a dot to follow the curve
        dot = Sphere(radius=0.1, color=PURE_RED)
        dot.move_to(points[0])
        
        # Add the curve and dot to the scene
        self.add(curve, dot)
        
        # Animate the dot following the curve
        self.play(
            MoveAlongPath(dot, curve),
            run_time=20,
            rate_func=linear
        )
        
        # Rotate the camera to show the 3D structure
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(10)
