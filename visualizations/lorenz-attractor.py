#  manim lorenz_attractor.py LorenzAttractor -pqh --disable_caching -p
#  rm /Users/markmorris/Documents/NPQG_Code_Base/NPQG/manim/media/videos/lorenz_attractor/1080p60/LorenzAttractor.mp4; manim lorenz_attractor.py LorenzAttractor -pqh --disable_caching -p
#  ported to ManimCE from https://github.com/fajrulfx/visualization101/blob/master/lorenz_attractor.py
from manim import *
import numpy as np

ELECTRIC_PURPLE = "#8F00FF"

class DotTrajectory:
    def __init__(self, start_pos, color):
        self.dot = Sphere(radius=0.05, color=color).move_to(start_pos)
        self.trajectory = VMobject(stroke_color=color, stroke_width=2, stroke_opacity=1)
        self.trajectory.start_new_path(self.dot.get_center())
        
    def update_position(self, mob, dt):
        x, y, z = mob.get_center()
        x_dot, y_dot, z_dot = self.lorenz(x * 10, y * 10, z * 10)
        SF = 25  # Increased scaling factor for smoother motion
        mob.shift((x_dot * dt / SF) * RIGHT + (y_dot * dt / SF) * UP + (z_dot * dt / SF) * OUT)
        
        # Update trajectory
        new_point = mob.get_center()
        if np.linalg.norm(new_point - self.trajectory.get_last_point()) > 0.01:
            self.trajectory.add_smooth_curve_to(new_point)
        
    def lorenz(self, x, y, z, s=10, r=28, b=2.667):
        x_dot = s * (y - x)
        y_dot = r * x - y - x * z
        z_dot = x * y - b * z
        return x_dot, y_dot, z_dot

class LorenzAttractor(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-3.5, 3.5],
            y_range=[-3.5, 3.5],
            z_range=[0, 3.5],
            axis_config={"include_tip": True, "include_ticks": True, "stroke_width": 2}
        )
        axes.shift(1.5 * UP)
        self.add(axes)

        labels = axes.get_axis_labels(
            Tex("x").scale(0.9),
            Tex("y").scale(0.9),
            Tex("z").scale(0.9)
        )
        labels[1].shift(2.5 * UP)
        self.add(labels)

        dots_info = [
            ([0, 0.1, 0.105], PURE_BLUE),
            ([0, 0.2, 0.210], PURE_RED)
        ]
        
        dots = [DotTrajectory(start_pos=pos, color=color) for pos, color in dots_info]

        self.set_camera_orientation(phi=65*DEGREES, theta=30*DEGREES, frame_center=1.5*UP)
        self.camera.background_color = ELECTRIC_PURPLE
        self.set_camera_orientation(zoom=0.7)
        self.begin_ambient_camera_rotation(rate=0.05)

        for dot in dots:
            dot.dot.add_updater(dot.update_position)
            self.add(dot.dot, dot.trajectory)

        self.wait(120)  # Increased wait time for a longer animation
