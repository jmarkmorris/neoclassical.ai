# NPQG Simulator

A simulator and visualizer for point potentials in 3D space following physical laws.

## Requirements

- Python 3.7+
- NumPy
- Manim (for visualization)

## Installation

1. Install the required packages:

```bash
pip install numpy manim
```

## Usage

### 1. Create a JSON Configuration File

Create a JSON file (e.g., `sim2.json`) with your simulation configuration. Here's an example:

```json
{
  "simulation": {
    "particles": [
      {
        "id": 1,
        "charge": 1,
        "position": [1.0, 0.0, 0.0],
        "velocity": [0.0, 0.1, 0.0]
      },
      {
        "id": 2,
        "charge": -1,
        "position": [-1.0, 0.0, 0.0],
        "velocity": [0.0, -0.1, 0.0]
      }
    ],
    "duration": 1000,
    "dt": 0.01
  },
  "visualization": {
    "colors": {
      "background": "#4B0082",
      "positive": "#FF0000",
      "negative": "#0000FF",
      "tracer": "#FFFFFF"
    },
    "marker_size": 0.1,
    "tracer": {
      "enabled": true,
      "history_length": 100,
      "fade": true
    },
    "sim_to_manim_ratio": 10,
    "manim_frame_rate": 30
  }
}
```

### 2. Run the Simulation

```bash
python run_animation.py --config sim2.json
```

This will:
1. Run the simulation using the configuration in `sim2.json`
2. Save the results to `simulation_results.json`
3. Generate a visualization of the simulation

### 3. Additional Options

- Run only the simulation without visualization:
  ```bash
  python run_simulation.py sim2.json --simulate-only
  ```

- Run only the visualization using an existing results file:
  ```bash
  python run_simulation.py simulation_results.json --visualize-only
  ```

- Specify a custom output file for the simulation results:
  ```bash
  python run_simulation.py sim2.json --output my_results.json
  ```

## System Architecture

1. **simulator.py**: Implements the physics simulation for point potentials
2. **visualizer.py**: Uses Manim to create 3D visualizations of the simulation results
3. **run_simulation.py**: Utility script to run the simulation and visualization

## JSON Configuration Parameters

### Simulation Parameters
- `particles`: List of particles with their initial properties
  - `id`: Unique identifier for the particle
  - `charge`: Charge value (positive or negative)
  - `position`: Initial 3D position [x, y, z]
  - `velocity`: Initial 3D velocity [dx/dt, dy/dt, dz/dt]
- `duration`: Duration of the simulation in time units
- `dt`: Time step size for the simulation

### Visualization Parameters
- `colors`: Color codes for various elements
  - `background`: Background color of the 3D space
  - `positive`: Color for positive charge particles
  - `negative`: Color for negative charge particles
  - `tracer`: Color for path tracers
- `marker_size`: Size of the particle markers
- `tracer`: Configuration for path tracers
  - `enabled`: Whether tracers are enabled
  - `history_length`: Number of history points to display
  - `fade`: Whether tracers should fade out
- `sim_to_manim_ratio`: Ratio of simulation steps to animation frames
- `manim_frame_rate`: Frame rate for the animation
