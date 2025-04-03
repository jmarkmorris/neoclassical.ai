# Useful
# manim -pqh --disable_caching example_scenes.py WriteStuff -p


# sourced from github manim repo example_scenes/basic.py

#!/usr/bin/env python


from manim import *
from tools import INDIGO, ELECTRIC_PURPLE

# To watch one of these scenes, run the following:
#
# Use the flag --quality l for a faster rendering at a lower quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have preview of the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the nth animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1920,1080
# for a 1920x1080 video)







class WriteStuff(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        
        example_text = Tex("This is some text", tex_to_color_map={"text": ELECTRIC_PURPLE})
        example_tex = MathTex(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange(DOWN)
        group.width = config["frame_width"] - 2 * LARGE_BUFF

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


