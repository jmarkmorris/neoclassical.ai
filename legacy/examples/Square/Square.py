import json
import random
from manim import *

# Define the list of colors for the random_color scheme
RANDOM_COLOR_OPTIONS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, PINK, TEAL, MAROON, GOLD, DARK_GRAY, GRAY, LIGHT_GRAY, WHITE, BLACK]


class TiledSquares(Scene):
    """
    A scene that tiles the Manim frame with colored squares in a grid pattern.
    The configuration is loaded from a JSON file.
    """
    def __init__(self, config_file="examples/Square.json", **kwargs):
        super().__init__(**kwargs)
        self.config_file = config_file
        self.config = self.load_config()
        self.square_size = self.config.get("square_size", 0.5)
        self.color_scheme = self.config.get("color_scheme", "alternating_red_blue")
        self.borders = self.config.get("borders", "yes") == "yes"
        self.opacity_variation = self.config.get("opacity_variation", "yes") == "yes"
        self.background_color = self.config.get("background_color", "WHITE")

    def load_config(self):
        """Loads the configuration from the JSON file."""
        with open(self.config_file, "r") as f:
            return json.load(f)

    def construct(self):
        """Constructs the scene by tiling the frame with colored squares."""
        try:
            if isinstance(self.background_color, str) and self.background_color.startswith("#"):
                self.camera.background_color = Color(self.background_color)
            else:
                self.camera.background_color = eval(self.background_color)
        except (NameError, TypeError):
            self.camera.background_color = WHITE
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
                if self.color_scheme == "alternating_red_blue":
                    color = PURE_RED if (i + j) % 2 == 0 else PURE_BLUE
                elif self.color_scheme == "black_and_white":
                    color = BLACK if (i + j) % 2 == 0 else WHITE
                elif self.color_scheme == "random_color":
                    color = random.choice(RANDOM_COLOR_OPTIONS)
                elif self.color_scheme == "random_red_blue":
                    color = random.choice([PURE_RED, PURE_BLUE])
                else:
                    color = WHITE # Default to white

                if self.opacity_variation:
                    opacity = random.uniform(0, 1)
                else:
                    opacity = 0.5  # Default opacity

                square.set_fill(color, opacity=opacity)
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
