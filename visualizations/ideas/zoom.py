# # manim zoom.py zoom -pqm --disable_caching -p

# from manim import *
# import random
# # import json

# INDIGO = "#4B0082"
# ELECTRIC_PURPLE = "#8F00FF"

# run_time = 3
# # run_time = 60
# frame_rate = 30
# # frame_rate = 60
# # paused = False # add pause feature?

# # powerpoint png export size
# config.pixel_width = 2998
# config.pixel_height = 1686
# config.frame_rate = frame_rate

# class photon(ThreeDScene):
#     def construct(self):
#         self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
#         self.camera.background_color = INDIGO


# how does zoom work?  on reddit they say scale self.camera.frame
# https://docs.manim.community/en/stable/reference/manim.scene.zoomed_scene.ZoomedScene.html


# from manim import *

# class zoom(ZoomedScene):
        
        # example
        # def construct(self):
        
        # dot = Dot().set_color(GREEN)
        # self.add(dot)
        # self.wait(1)
        # self.activate_zooming(animate=False)
        # self.wait(1)
        # self.play(dot.animate.shift(LEFT))

        # example
        # def __init__(self, **kwargs):
        #     ZoomedScene.__init__(
        #         self,
        #         zoom_factor=0.3,
        #         zoomed_display_height=1,
        #         zoomed_display_width=3,
        #         image_frame_stroke_width=20,
        #         zoomed_camera_config={
        #             "default_frame_stroke_width": 3,
        #         },
        #         **kwargs
        #     )

        # def construct(self):
        #     dot = Dot().set_color(GREEN)
        #     sq = Circle(fill_opacity=1, radius=0.2).next_to(dot, RIGHT)
        #     self.add(dot, sq)
        #     self.wait(1)
        #     self.activate_zooming(animate=False)
        #     self.wait(1)
        #     self.play(dot.animate.shift(LEFT * 0.3))

        #     self.play(self.zoomed_camera.frame.animate.scale(4))
        #     self.play(self.zoomed_camera.frame.animate.shift(0.5 * DOWN))


