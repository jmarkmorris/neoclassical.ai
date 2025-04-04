from manim import *
import random
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
class MultipleAnimations(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Multiple Concurrent Animations",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "AnimationGroup(Write(text), Rotating(square)) with updaters for dynamic effects",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        animation_configs = [
            {"location": (-2, 1.5, 0)},  # Moved right from x=-4 to x=-2
            {"location": (2, 1.5, 0)},   # Moved left from x=4 to x=2
            {"location": (-2, -2, 0)},   # Moved right from x=-4 to x=-2
            {"location": (2, -2, 0)},    # Moved left from x=4 to x=2
        ]
        
        colors = [PURE_BLUE, PURE_RED, WHITE, PURPLE]
        words = ["Hello", "World!", "Nature", "Emerges!!"]
        
        # Set common properties
        for i, config in enumerate(animation_configs):
            config["font"] = "Helvetica Neue"
            config["font_size"] = 24  # Reduced font size from 32 to 24
            config["typing_speed"] = 0.5
            config["color"] = colors[i]
            config["text"] = words[i]
        
        text_objects = []  
        square_objects = []
        
        for config in animation_configs:
            # Create text object and center it vertically in the square
            text = Text(
                config["text"],
                font="Helvetica Neue",
                weight="LIGHT",
                font_size=config["font_size"],
                color=config["color"]
            ).move_to(config["location"] + DOWN * 0.5)  # Move down to center in square
            
            text_objects.append(text)

            # Define text update function
            def update_animation(obj, dt, config_dict):
                current_length = len(obj.text)
                target_length = len(config_dict["text"])
                if current_length < target_length:
                    obj.become(
                        Text(
                            config_dict["text"][:current_length + 1], 
                            font="Helvetica Neue",
                            weight="LIGHT",
                            font_size=config_dict["font_size"],
                            color=obj.color
                        ).move_to(obj.get_center())  # Maintain the same position
                    )

            # Add updater to text
            text.add_updater(lambda obj, dt, config_dict=config: update_animation(obj, dt, config_dict))
            self.add(text)

            # Create square animation - smaller and moved down
            square = Square().move_to(config["location"] + DOWN * 0.5).scale(0.9)
            square_objects.append(square)
            
            # Define square rotation updater
            def update_square_rotation(obj, dt):
                obj.rotate(0.1 * dt, about_point=obj.get_center())

            square.add_updater(update_square_rotation)
            self.add(square)
        
        # Create animation groups
        text_animations = AnimationGroup(
            *[Write(text, run_time=len(config["text"]) * config["typing_speed"]) 
              for text, config in zip(text_objects, animation_configs)]
        )
        
        square_animations = AnimationGroup(
            *[Rotating(square, about_point=square.get_center()) 
              for square in square_objects]
        )
        
        # Play animations concurrently
        self.play(AnimationGroup(text_animations, square_animations))
        self.wait()
