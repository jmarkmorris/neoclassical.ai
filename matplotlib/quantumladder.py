import numpy as np
import matplotlib.pyplot as plt
import random

class Segment:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def generate(self, x_start, y_start):
        x = np.linspace(self.start, self.end, 100)
        y = np.sin(x)
        y += y_start - y[0]  # Adjust y to start at the given y_start
        x += x_start - self.start  # Adjust x to start at the correct position
        return x, y

# Define the segments of y = sin(x)
segments = {
    't': Segment(np.pi / 4, 3 * np.pi / 4),
    'd': Segment(3 * np.pi / 4, 5 * np.pi / 4),
    'b': Segment(5 * np.pi / 4, 7 * np.pi / 4),
    'u': Segment(7 * np.pi / 4, 9 * np.pi / 4)
}

# Define allowed transitions
allowed_transitions = {
    'b': ['u'],
    'u': ['u', 't'],
    't': ['d'],
    'd': ['d', 'b']
}

# Function to generate the full curve based on segments
def generate_curve(N_max):
    x_vals = []
    y_vals = []
    current_y_start = 0
    current_segment = 'b'  # Start with 'b'

    for N in range(N_max):

        if current_segment in segments:
            segment = segments[current_segment]
            
            x1 = np.pi / 4 + N * np.pi / 2
            x_segment, y_segment = segment.generate(x1, current_y_start)

            # Update the starting y value for the next segment
            current_y_start = y_segment[-1]

        else:
            continue

        x_vals.extend(x_segment)
        y_vals.extend(y_segment)
        
        # Add a gap to introduce potential discontinuity (if needed)
        x_vals.append(np.nan)
        y_vals.append(np.nan)
        
        # Randomly choose the next segment based on allowed transitions
        current_segment = random.choice(allowed_transitions[current_segment])

    return np.array(x_vals), np.array(y_vals)

# Number of segments to display
xpi = 32
N_max = 2*xpi

# Generate the curve
x_vals, y_vals = generate_curve(N_max)

# Plot the curve
plt.figure(figsize=(12, 6))
plt.plot(x_vals, y_vals)

# Customize x-axis to show units of pi/4
plt.xticks(np.arange(0, np.pi * (xpi + 2), np.pi), [f'{i}$\\pi$' for i in range(xpi + 2)])

plt.ylabel('y')
plt.xlabel('x')
plt.title('Binary Potential Wells')
plt.grid(True, which='both', axis='both')

plt.show()

