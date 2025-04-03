from manim import *
import random
from tools import INDIGO

class MultipleAnimations(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        animation_configs = [
            {"location": (-4, 2, 0)},
            {"location": (4, 2, 0)},
            {"location": (-4, -2, 0)},
            {"location": (4, -2, 0)},
        ]
        
        colors = [PURE_BLUE, PURE_RED, WHITE, PURPLE]
        words = ["Hello", "World!", "Nature", "Emerges!!"]
        
        # Set common properties
        for i, config in enumerate(animation_configs):
            config["font"] = "Helvetica Neue"
            config["font_size"] = 32
            config["typing_speed"] = 0.5
            config["color"] = colors[i]
            config["text"] = words[i]
        
        text_objects = []  
        square_objects = []
        
        for config in animation_configs:
            # Create text object
            text = Text(
                config["text"],
                font=config["font"],
                font_size=config["font_size"],
                color=config["color"]
            ).move_to(config["location"])
            
            text_objects.append(text)

            # Define text update function
            def update_animation(obj, dt, config_dict):
                current_length = len(obj.text)
                target_length = len(config_dict["text"])
                if current_length < target_length:
                    obj.become(
                        Text(
                            config_dict["text"][:current_length + 1], 
                            font=obj.font, 
                            color=obj.color
                        ).move_to(obj.get_center())
                    )

            # Add updater to text
            text.add_updater(lambda obj, dt, config_dict=config: update_animation(obj, dt, config_dict))
            self.add(text)

            # Create square animation
            square = Square().move_to(config["location"]).scale(1.25)
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
