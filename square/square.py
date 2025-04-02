import json
import random
from manim import *

RED = RED
GREEN = GREEN
BLUE = BLUE
YELLOW = YELLOW
ORANGE = ORANGE
PURPLE = PURPLE
PINK = PINK
TEAL = TEAL
MAROON = MAROON
GOLD = GOLD
DARK_GRAY = DARK_GRAY
GRAY = GRAY
LIGHT_GRAY = LIGHT_GRAY
WHITE = WHITE
BLACK = BLACK


class TiledSquares(Scene):
    """
    A scene that tiles the Manim frame with colored squares in a grid pattern.
    The configuration is loaded from a JSON file.
    """
    def __init__(self, config_file="square.json", **kwargs):
        super().__init__(**kwargs)
        self.config_file = config_file
        self.config = self.load_config()
        self.square_size = self.config.get("square_size", 0.5)
        self.color_scheme = self.config.get("color_scheme", "alternating_red_blue")
        self.borders = self.config.get("borders", "yes") == "yes"

    def load_config(self):
        """Loads the configuration from the JSON file."""
        with open(self.config_file, "r") as f:
            return json.load(f)

    def construct(self):
        """Constructs the scene by tiling the frame with colored squares."""
        frame_width = self.camera.frame_width
        frame_height = self.camera.frame_height

        num_squares_x = int(frame_width // self.square_size)
        num_squares_y = int(frame_height // self.square_size)

        squares = VGroup()
        for i in range(num_squares_x):
            for j in range(num_squares_y):
                x = (i - num_squares_x / 2 + 0.5) * self.square_size
                y = (j - num_squares_y / 2 + 0.5) * self.square_size
                square = Square(side_length=self.square_size, stroke_width=1)
                if not self.borders:
                    square.set_stroke(width=0)
                square.move_to([x, y, 0])

                # Color scheme logic
                color_schemes = {
                    "alternating_red_blue": [PURE_RED, PURE_BLUE],
                    "black_and_white": [BLACK, WHITE],
                    "random_color": [random.choice([RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, PINK, TEAL, MAROON, GOLD, DARK_GRAY, GRAY, LIGHT_GRAY, WHITE, BLACK])] * 2,  # Use same random color for both
                    "random_red_blue": [random.choice([PURE_RED, PURE_BLUE])] * 2 # Randomly choose RED or BLUE for each square
                }

                colors = color_schemes.get(self.color_scheme, [WHITE, WHITE])  # Default to white
                if self.color_scheme == "random_red_blue":
                    square.set_fill(colors[0], opacity=1)
                else:
                    square.set_fill(colors[(i + j) % 2], opacity=1)

                squares.add(square)

        self.add(squares)

        # Title with BLACK background
        title = Text(f"Square Size: {self.square_size}", color=WHITE)
        title_background = Rectangle(
            width=title.width + 0.5, height=title.height + 0.2, color=BLACK, fill_opacity=1
        )
        title_background.move_to(title.get_center())
        title_background.shift(UP * 3.5)
        title.shift(UP * 3.5)
        title_group = VGroup(title_background, title)
        self.add(title_group)
