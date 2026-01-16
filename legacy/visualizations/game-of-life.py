# manim -pqh --disable_caching game_of_life.py game_of_life -p

from manim import *
import copy
import random
import numpy as np

frame_rate = 60
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate
frames_rendered = 12000
frames_per_update = 12
frame_width = 14
frame_height = 8

ELECTRIC_PURPLE = "#8F00FF"
DEEP_PURPLE = "#47015D"
TRUE_PURPLE = "#6A0DAD"
INDIGO = "#4B0082"

cells_x = 70
cells_y = 40
cell_side = 0.2

def evolve(input_grid):
    input_grid = np.array(input_grid)
    output_grid = np.zeros_like(input_grid)
    # Create a padded version of the input grid to handle edge cases
    padded_grid = np.pad(input_grid, 1, mode='constant')
    # Compute the sum of neighbors for each cell
    neighbor_sum = sum(np.roll(np.roll(padded_grid, i, 0), j, 1)[1:-1, 1:-1]
                       for i in (-1, 0, 1) for j in (-1, 0, 1)
                       if (i != 0 or j != 0))
    # Update the output grid based on the neighbor sum and the rules of the game
    output_grid[(input_grid == 1) & ((neighbor_sum < 2) | (neighbor_sum > 3))] = 0
    output_grid[(input_grid == 1) & ((neighbor_sum == 2) | (neighbor_sum == 3))] = 1
    output_grid[(input_grid == 0) & (neighbor_sum == 3)] = 1
    return output_grid.tolist()

class game_of_life(Scene):
    def construct(self):
        # Create a grid of cells
        cells = []
        for i in range(cells_x):
            row = []
            for j in range(cells_y):
                cell = Square(side_length=cell_side, color=ELECTRIC_PURPLE, stroke_width=1, fill_opacity=0)
                cell.move_to([-(frame_width - cell_side)/2 + i * cell_side, -(frame_height - cell_side)/2 + j * cell_side, 0])
                self.add(cell)
                row.append(cell)
            cells.append(row)

        grid1 = [[random.choice([0, 1]) for j in range(cells_y)] for i in range(cells_x)]
        grid2 = evolve(grid1)

        current_gen = grid1
        next_gen = grid2

        frame_count = 0

        while frame_count < frames_rendered:
            if frame_count % frames_per_update == 0:
                self.update_colors(cells, current_gen)
                current_gen, next_gen = next_gen, current_gen
                next_gen = evolve(current_gen)
            self.wait(1/frame_rate)
            frame_count += 1

    def update_colors(self, cells, grid):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                cells[i][j].set_fill(TRUE_PURPLE if grid[i][j] == 1 else ELECTRIC_PURPLE, opacity=1 if grid[i][j] == 1 else 0)



