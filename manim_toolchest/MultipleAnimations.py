# manim -pqh --disable_caching MultipleAnimations.py MultipleAnimations -p

# this is an example of multiple concurrent animations each defined by a dictionary.
# todo : try to do this with dots, each orbiting the origin of their system.

from manim import *
import random
from tools import INDIGO

class MultipleAnimations(Scene):
    def construct(self):
        # Set background color to INDIGO
        self.camera.background_color = INDIGO
        
        dictionary_of_animations = [
            {
                "location": (-4, 2, 0),
            },
            {
                "location": (4, 2, 0),
            },
            {
                "location": (-4, -2, 0),
            },
            {
                "location": (4, -2, 0),
            },
            # Add more dictionaries for additional animations
        ]
        MyColors = [PURE_BLUE, PURE_RED, WHITE, PURPLE]
        MyWords = ["Hello", "World!", "Nature", "Emerges!!"]
        # Best practice for repetitive dictionary items
        for i, D in enumerate(dictionary_of_animations):
            D["font"] = "Helvetica Neue"
            D["font_size"] = 32
            D["typing_speed"] = 0.5
            D["color"] = MyColors[i]
            D["text"] = MyWords[i]
        
        Alist = []  
        square_list = []  # List to store square animations


        for D in dictionary_of_animations:
            A = Text(
                D["text"],
                font=D["font"],
                font_size=D["font_size"],
                color=D["color"]
            ).move_to(D["location"])
            
            Alist.append(A)

            def update_animation(obj, dt, D_):
                current_length = len(obj.text)  # Access the attribute directly
                target_length = len(D_["text"])
                if current_length < target_length:
                    obj.become(Text(D_["text"][:current_length + 1], font=obj.font, color=obj.color).move_to(obj.get_center()))

            A.add_updater(lambda obj, dt, D_=D: update_animation(obj, dt, D_))  # Pass the dictionary entry as an argument
            self.add(A)

            # Creating a rotating square animation
            square_animation = Square().move_to(D["location"]).scale(1.25)
            square_list.append(square_animation)
            
            def update_square_rotation(obj, dt):
                obj.rotate(0.1 * dt, about_point=obj.get_center())  # Adjust the rotation speed as needed

            square_animation.add_updater(update_square_rotation)
            
            self.add(square_animation)
        
        text_animations_group = AnimationGroup(*[Write(A, run_time=len(D["text"]) * D["typing_speed"]) for A, D in zip(Alist, dictionary_of_animations)])
        square_animations_group = AnimationGroup(*[Rotating(square, about_point=square.get_center()) for square in square_list])
        
        self.play(AnimationGroup(text_animations_group, square_animations_group))  # Play both AnimationGroups concurrently
        self.wait()
    
