from manim import *
import numpy as np
from tools import INDIGO, ELECTRIC_PURPLE

class Lorenz3D(ThreeDScene):
    """Visualization of the Lorenz attractor in 3D space"""
    
    def construct(self):
        # Set up camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.camera.frame_center = ORIGIN
        
        # Add title and subtitle
        title = Text(
            "Lorenz Attractor Visualization",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_corner(UL)
        
        subtitle = Text(
            "MoveAlongPath(dot, curve) with Euler method trajectory",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.3)
        
        self.add_fixed_in_frame_mobjects(title, subtitle)
        
        # Lorenz system parameters
        sigma = 10
        beta = 8/3
        rho = 28
        
        # Lorenz differential equations
        def lorenz_deriv(xyz, t0, sigma=sigma, beta=beta, rho=rho):
            x, y, z = xyz
            return [
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ]
        
        # Create 3D axes
        axes = ThreeDAxes(
            x_range=[-30, 30, 5],
            y_range=[-30, 30, 5],
            z_range=[0, 60, 10],
            x_length=6,
            y_length=6,
            z_length=6,
            axis_config={"include_tip": True, "include_ticks": True}
        )
        
        # Add labels
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        z_label = axes.get_z_axis_label("z", edge=OUT, direction=OUT)
        
        # Add elements to scene
        self.add(axes, x_label, y_label, z_label)
        
        # Generate Lorenz attractor trajectory
        dt = 0.01
        num_steps = 10000
        xyz = np.array([0.1, 0.0, 0.0])  # Initial conditions
        
        # Create curve object
        curve = VMobject(stroke_width=2, stroke_color=ELECTRIC_PURPLE)
        points = [axes.coords_to_point(*xyz)]
        
        # Compute trajectory points using Euler method
        for _ in range(num_steps):
            dxyz = lorenz_deriv(xyz, 0)
            xyz = xyz + np.array(dxyz) * dt
            points.append(axes.coords_to_point(*xyz))
        
        # Set curve points
        curve.set_points_smoothly(points)
        
        # Create tracking sphere
        dot = Sphere(radius=0.1, color=PURE_RED).move_to(points[0])
        
        # Add curve and dot to scene
        self.add(curve, dot)
        
        # Animate dot following the curve
        self.play(
            MoveAlongPath(dot, curve),
            run_time=20,
            rate_func=linear
        )
        
        # Rotate camera to show 3D structure
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(10)
