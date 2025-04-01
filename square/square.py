import json
import random
from manim import *

class TiledSquares(Scene):
    def __init__(self, config_file="square/square.json", **kwargs):
        super().__init__(**kwargs)
        self.config_file = config_file
        self.config = self.load_config()
        self.square_size = self.config.get("square_size", 0.5)
        self.color_scheme = self.config.get("color_scheme", "alternating_red_blue")

    def load_config(self):
        with open(self.config_file, "r") as f:
            return json.load(f)

    def construct(self):
        frame_width = config["frame_width"]
        frame_height = config["frame_height"]

        num_squares_x = int(frame_width // self.square_size)
        num_squares_y = int(frame_height // self.square_size)

        squares = VGroup()
        for i in range(num_squares_x):
            for j in range(num_squares_y):
                x = (i - num_squares_x / 2) * self.square_size + self.square_size / 2
                y = (j - num_squares_y / 2) * self.square_size + self.square_size / 2
                square = Square(side_length=self.square_size, stroke_width=1)
                square.move_to([x, y, 0])

                if self.color_scheme == "alternating_red_blue":
                    if (i + j) % 2 == 0:
                        square.set_fill(PURE_RED, opacity=1)
                    else:
                        square.set_fill(PURE_BLUE, opacity=1)
                elif self.color_scheme == "black_and_white":
                    if (i + j) % 2 == 0:
                        square.set_fill(BLACK, opacity=1)
                    else:
                        square.set_fill(WHITE, opacity=1)
                elif self.color_scheme == "random_color":
                    square.set_fill(random.choice(list(ManimColor)), opacity=1)
                else:
                    square.set_fill(WHITE, opacity=0.5)  # Default color

                squares.add(square)

        self.add(squares)

        # Title with INDIGO background
        title = Text(f"Square Size: {self.square_size}", color=WHITE)
        title_background = Rectangle(
            width=title.width + 0.5, height=title.height + 0.2, color=INDIGO, fill_opacity=1
        )
        title_group = VGroup(title_background, title).move_to(UP * 3.5)
        self.add(title_group)
