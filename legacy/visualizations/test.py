# manim -pqh --disable_caching test.py test -p

from manim import *

class test(ThreeDScene):
    def construct(self):
        # create a circle and a square
        circle = Circle()
        square = Square()
        # rotate the square by 90 degrees
        # square.rotate(PI/2)
        # create an animation group with the circle and the square
        group = AnimationGroup(Create(circle), Create(square), run_time=3, rate_func=smooth)
        # animate the group to rotate around the z axis
        # rotating_group = Rotating(group, axis=OUT)
        # play the animation
        self.play(group)