### Project Goals

The goal is to create a python/manim program `Square.py` that generates a 2D image that tiles a manim frame with small colored squares in a grid pattern.

## Frame design

- Calculate the number of squares that will fit horizontally and vertically based on the square size and the frame size.
- Create a grid of colored squares with the grid centered on the origin.

## Input specification

A json input file, `Square.json`, specifies the following:

- The square size
- The color scheme
- Borders (yes/no)
- Opacity Variation (yes/no)
- Background Color (name or hex code)

The run_example.sh script provides a menu to select these options, updating the `Square.json` file before running `Square.py`.

## Color schemes

The json input file specifies a color scheme to be used, chosen from the following options:

- `alternating_red_blue`: Alternating PURE_RED and PURE_BLUE both horizontally and vertically (like squares on a chess board).
- `black_and_white`: Alternating black and white.
- `random_color`: Each square is assigned a random color chosen from a predefined list of Manim colors.
- `random_red_blue`: Each square is randomly assigned either PURE_RED or PURE_BLUE.

## Opacity Variation

The script asks whether to disable opacity variation. If disabled, all squares have an opacity of 0.5. If enabled (default), each square has a random opacity between 0 and 1.

## Background Color

The background color can be specified in the `Square.json` file using either a color name defined in Manim (e.g., "WHITE", "BLACK", "INDIGO") or a hex code (e.g., "#4B0082").

## Titles

The title on the image shall have a solid BLACK background with white letters that indicate the square size used in the image.

## Run file

- The run_example.sh script presents a menu to choose the square size and color scheme.
- It updates the `Square.json` file with the selected options.
- It then calls the `Square.py` program to generate the image.
- The run file also allows you to choose whether or not to display borders on the squares.
- The run file also allows you to choose whether or not to display opacity variation on the squares.

## Simplicity

This is a simple program, so keep it simple.
