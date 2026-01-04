# manim emergence_experiment2.py emergence -pqh --disable_caching -p
#
# This program is used for Experiment 1
#
from manim import *
import random
import itertools
from colour import Color
import math
import sys

config.frame_rate = 60
# num_vertices = 24
# num_vertices = 12  # add the ingredients for a fermion and see what happens
num_vertices = 32
dot_radius = 0.02

class ColoredDot(Dot):
    def __init__(self, color, coordinates, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.coordinates = coordinates

# class Bzzzt(Line):
#    def __init__(self, start, end, **kwargs):
#       super().__init__(start, end, color=Color("#8F00FF"), stroke_width=10, **kwargs)

def get_next_coordinates(graph, velocities, vertex_key, dt):
    current_coordinates = graph.vertices[vertex_key].get_center()
    displacement = np.array([0.0, 0.0, 0.0])
    for other_vertex_key in graph.vertices:
        if other_vertex_key == vertex_key:
            continue  #  the > @ could go here in the ultimate simulation.
        other_vertex_coordinates = graph.vertices[other_vertex_key].get_center()
        direction = other_vertex_coordinates - current_coordinates
        direction = direction / np.linalg.norm(direction)
        distance = np.linalg.norm(other_vertex_coordinates - current_coordinates)

        velocity = velocities[vertex_key]
        
        dsquare = max(0.6, distance * distance) # temporary shim to prevent velocity from blowing up
        if dt > 0:
            if graph.vertices[vertex_key].color == graph.vertices[other_vertex_key].color:
                new_velocity = 0.99 * velocity - 0.003 * direction / (dsquare * dt)
                displacement += new_velocity * dt
            else:
                new_velocity = 0.99 * velocity + 0.003 * direction / (dsquare * dt)
                displacement += new_velocity * dt
            velocities[vertex_key] = new_velocity

    next_coordinates = current_coordinates + displacement
    # Wrap the coordinates.  Need to check or test the math.  this is going to cause problems. moving a charge is problematic. Need to keep track of all points and only lot those in the window. 
    # eventually allow window to move?
    if next_coordinates[0] <= -7 or next_coordinates[0] >= 7:
        next_coordinates[0] = ((next_coordinates[0] + 7) % 14) - 7

    if next_coordinates[1] <= -4 or next_coordinates[1] >= 4:
        next_coordinates[1] = ((next_coordinates[1] + 4) % 8) - 4

    next_coordinates[2] = 0

    return next_coordinates

class emergence(Scene):
    def construct(self):

        colors = [PURE_RED, PURE_BLUE]
        # x_range = (-6, 6)
        # x_range = (-5, 5)
        # x_range = (-4, 4)
        # x_range = (-3, 3)
        # x_range = (-2, 2)
        x_range = (-6, 6)

        # y_range = (-3, 3)
        # y_range = (-2, 2)
        y_range = (-3, 3)
        # y_range = (-0.5, 0.5)
        # y_range = (-0.25, 0.25)
        # y_range = (-0.1, 0.1)

        vertices = {f'v{i}': ColoredDot(colors[i % 2], [random.uniform(*x_range), random.uniform(*y_range), 0]) for i in range(num_vertices)}
        vertex_config = {v: {'color': vertices[v].color, 
                             'stroke_width': 1, 
                             'fill_opacity': 1, 
                             'radius': dot_radius} for v in vertices}
        layout = {}
        layout = {v: vertices[v].coordinates for v in vertices}
        
        # the animation fails if velocity is too high. Not sure why. Possible bug.
        # VelocityMultiplier = 0.1 * math.pow(10, 0) # experiment to see if this will reduce the energy. It didn't seem to make a difference. Interesting.
        # VelocityMultiplier = 0.01 * math.pow(10, 0) 
        VelocityMultiplier = math.pow(10, 0) 
        # VelocityMultiplier = 3 * math.pow(10, 0) 
        # velocities = {f'v{i}': np.array([(random.choice([-1, 1]) * random.uniform(.1, .15) * VelocityMultiplier) if j != 2 else 0 for j in range(3)]) for i in range(num_vertices)}
        velocities = {f'v{i}': np.array([(random.choice([-1, 1]) * random.uniform(.1, .2) * VelocityMultiplier) if j != 2 else 0 for j in range(3)]) for i in range(num_vertices)}

        edges = list(itertools.combinations(vertices.keys(), 2))
        edge_config = {
            edge: {
                'color': vertices[edge[0]].color if vertices[edge[0]].color == vertices[edge[1]].color 
                        else Color("#8F00FF"),   # Electric Purple!
                'stroke_width': 1 # 1.5 is good if focused on relationships, but overpowers the vertices.
            } for edge in edges
        }

        G = Graph(vertices.keys(), 
                  edges, 
                  layout=layout, 
                  vertex_config=vertex_config, 
                  edge_config=edge_config)
        
        rect = Rectangle(
            color=WHITE,
            fill_opacity=0,
            stroke_width=4,
            height=8,
            width=14
        )
        
        self.add(rect)
        
        self.play(Create(G))
        
        def update_vertices(mob, dt):
            
            # Calculate the next positions of all vertices
            next_positions = {}
            for vertex in mob.vertices:
                next_positions[vertex] = get_next_coordinates(mob, velocities, vertex, dt)

            # Move all vertices to their next positions
            for vertex in mob.vertices:
                mob.vertices[vertex].move_to(next_positions[vertex])

        G.add_updater(update_vertices)

        # this controls the video length
        self.wait(59)


        # add a way to keep the history of per frame location for each architrino so they can be drawn as well
