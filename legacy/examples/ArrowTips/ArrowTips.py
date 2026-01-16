from manim import *
INDIGO = "#4B0082"

class ArrowTips(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Arrow Tips Showcase",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Axes(axis_config={'tip_shape': ArrowTipClass}) with different tip styles",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
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
            y_pos = 0.5 - (i // 4) * 2.5  # Reduced vertical spacing to move bottom row up
            
            ax.move_to([x_pos, y_pos, 0])
            self.add(ax)

            # Add label with tip shape name
            label = Text(tip_shapes[i].__name__, font="Helvetica Neue", weight="LIGHT", font_size=24)
            label.next_to(ax, UP)
            self.add(label)


