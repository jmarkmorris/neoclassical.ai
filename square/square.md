### Project Goals

The goal is to create a python/manim program `square.py` that generates a 2D image that tiles a manim frame with small colored squares in a grid pattern.

## Frame design

- Calculate the number of squares that will fit horizontally and vertically based on the square size and the frame size.
- Create a grid of colored squares with the grid centered on the origin.

## Input specification

A json input file, `square/square.json`, specifies the following:

- The square size
- The color scheme
- Borders (yes/no)

The `run_square.sh` script provides a menu to select these options, updating the `square/square.json` file before running `square.py`.

## Color schemes

The json input file specifies a color scheme to be used, chosen from the following options:

- `alternating_red_blue`: Alternating PURE_RED and PURE_BLUE both horizontally and vertically (like squares on a chess board).
- `black_and_white`: Alternating black and white.
- `random_color`: Each square a random manim color.
- `random_red_blue`: Each square is randomly either RED or BLUE.

## Titles

The title on the image shall have a solid BLACK background with white letters that indicate the square size used in the image.

## Run file

- The `run_square.sh` script presents a menu to choose the square size and color scheme.
- It updates the `square/square.json` file with the selected options.
- It then calls the `square.py` program to generate the image.
- The run file has comments that specify the smallest and largest square sizes possible in manim.
- The run file also allows you to choose whether or not to display borders on the squares.

## Simplicity

This is a simple program, so keep it simple.
