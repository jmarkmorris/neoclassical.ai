## manim ArrowTips.py ArrowTips -pqh --disable_caching -p

from manim import *
from tools import INDIGO

class ArrowTips(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        

        tip_shapes = [ArrowTriangleTip, ArrowTriangleFilledTip, ArrowSquareTip, ArrowSquareFilledTip, ArrowCircleTip, ArrowCircleFilledTip, StealthTip]
        axes = []
        for tip_shape in tip_shapes:
            kwargs = {
                'x_range': [-1,1,1],
                'y_range': [-1,1,1],
                'x_length': 1.5,
                'y_length': 1.5,
                'axis_config': {
                    'tip_shape': tip_shape
                }
            }
            ax = Axes(**kwargs)
            axes.append(ax)
        for i, ax in enumerate(axes):
            ax.shift(3.25 * RIGHT * (i % 4) + 3.5 * DOWN * (i // 4) + 1.5*UP + 5*LEFT)
            self.add(ax)

            label = Text(tip_shapes[i].__name__, font_size=24)
            label.next_to(ax, UP)
            self.add(label)


