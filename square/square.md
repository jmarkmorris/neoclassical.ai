### Project Goals

The goal is to create a python/manim program square.py that generates a 2D *image* that tiles a manim frame with small colored squares in a grid pattern. 

## Frame design

- calculate the number of squares that will fit horizontally and vertically based on the square size and the frame size 
- create a grid of colored squares with the grid centered on the origin

## Input specification

A json input file, square.json, specifies the following:

- the square size
- the color scheme

## Color schemes

The json input file specifies a color scheme to be used, chosen from the following options.

- Alternating PURE_RED and PURE_BLUE both horizontally and vertically (like squares on a chess board)
- Alternating black and white
- Each square a random manim color

## Titles

The title on the image shall have a solid INDIGO background with white letters that indicate the square size used in the image.

## Run file

- the run file will call the program square.py program to generate the image.
- the run file will have comment that specifies the smallest square possible in manim.
- the run file will have a comment that specifies the largest square size that will fit. One square in this case!

## Simplicity

This is a simple program so keep it simple.