from manim import *
from tools import INDIGO

class ArrowTips(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Define all arrow tip types to display
        tip_shapes = [
            ArrowTriangleTip, 
            ArrowTriangleFilledTip, 
            ArrowSquareTip, 
            ArrowSquareFilledTip, 
            ArrowCircleTip, 
            ArrowCircleFilledTip, 
            StealthTip
        ]
        
        axes = []
        
        # Create axes with different tip shapes
        for tip_shape in tip_shapes:
            kwargs = {
                'x_range': [-1, 1, 1],
                'y_range': [-1, 1, 1],
                'x_length': 1.5,
                'y_length': 1.5,
                'axis_config': {
                    'tip_shape': tip_shape
                }
            }
            ax = Axes(**kwargs)
            axes.append(ax)
        
        # Position axes in a grid layout
        for i, ax in enumerate(axes):
            # Calculate position based on index
            x_pos = (i % 4) * 3.25 - 5
            y_pos = 1.5 - (i // 4) * 3.5
            
            ax.move_to([x_pos, y_pos, 0])
            self.add(ax)

            # Add label with tip shape name
            label = Text(tip_shapes[i].__name__, font_size=24)
            label.next_to(ax, UP)
            self.add(label)


