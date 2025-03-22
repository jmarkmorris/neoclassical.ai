# NPQG Simulator and Visualizer

A simulator and visualizer for point potentials in 3D space following provided action laws, which may be physics based or geometry based. This project uses Python with Manim to create animations of particle interactions based on configurable action models.

## Overview

The NPQG Simulator is designed to simulate the movement of point potentials (particles) in 3D space according to physics defined by action functions. The simulation results are then visualized using Manim to create engaging animations of the particle interactions.

Key features:

- Discrete time simulation with configurable action functions
- 3D visualization with Manim
- Two point potential particle types with opposite potential polarity
- Path history tracers for particles
- Dynamic scaling to keep particles in view
- Pluggable action functions for different physical and geometry models
- Comprehensive configuration system with sensible defaults

## Requirements

- Python 3.7+
- NumPy
- Manim (for visualization)

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Ensure Manim dependencies are installed (see [Manim installation guide](https://docs.manim.community/en/stable/installation.html))

## Project Structure

- `simulator.py`: Core simulation engine implementing physics calculations
- `visualizer.py`: 3D visualization of simulation results using Manim
- `run_animation.py`: Utility script to run both simulation and visualization
- `action_basic.py`: Default action function for physics calculations
- `example_config.json`: Example configuration file with all available options
- Custom action functions can be added as `action_<name>.py` files

## Usage

### Basic Usage

Run a simulation and visualization with the default configuration:

```bash
python run_animation.py
```

Run with a specific configuration file:

```bash
python run_animation.py --config my_config.json
```

### Command Line Options

```bash
python run_animation.py --help
```

Options include:

- `--config`, `-c`: Path to configuration file (default: sim30.json)
- `--output`, `-o`: Path to save simulation results (default: simulation_results.json)
- `--simulate-only`: Run simulation only, without visualization
- `--visualize-only`: Run visualization only, using existing results file
- `--quality`, `-q`: Quality setting for visualization (l=low, m=medium, h=high, k=4K)
- `--no-preview`: Don't open preview window after rendering

### Simulation Only

To run just the simulation:

```bash
python simulator.py my_config.json output_file.json
```

### Visualization Only

To visualize existing simulation results:

```bash
python run_animation.py --visualize-only --output existing_results.json
```

## Creating Custom Configurations

Create a JSON file with your desired settings. See the `example_config.json` for a complete example with all available options.

The minimum required configuration is a list of particles with their initial properties:

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
    ]
  }
}
```

All other parameters will use their default values when not specified.

## Action Functions

Action functions define how particles interact and move. The system is designed to support multiple action functions, allowing for different physics models:

1. Create a new Python file named `action_<name>.py`
2. Implement a class named `Action<Name>` (with capitalized name)
3. The class must have:
   - An `__init__` method that accepts a configuration parameter
   - An `apply` method that accepts a list of particles and a time step

See `action_basic.py` for an example implementation.

To use a custom action function, specify it in the configuration:

```json
{
  "simulation": {
    "action_function": "your_action_name"
  }
}
```

## Configuration System

The simulator uses a robust configuration system with sensible defaults for all parameters. You only need to specify the parameters you want to customize in your JSON configuration file. The system will automatically merge your configuration with the default values.

See `example_config.json` for a complete example with all available options.

## Configuration Parameters

All configuration parameters are now included in every config file (sim2.json, sim30.json) with their default values, ensuring consistent behavior across different simulation configurations.

### Simulation Parameters
- `simulation`: Main simulation settings
  - `particles`: List of particles with their initial properties
    - `id`: Unique identifier for the particle
    - `charge`: Charge value (positive or negative)
    - `position`: Initial 3D position [x, y, z]
    - `velocity`: Initial 3D velocity [dx/dt, dy/dt, dz/dt]
  - `duration`: Duration of the simulation in time units (default: 10.0)
  - `dt`: Time step size for the simulation (default: 0.01)
  - `max_history`: Maximum number of history points to store for each particle (default: 10000)
  - `action_function`: Specifies which action function to use for physics calculations (default: "basic")

### Physics Parameters
- `physics`: Physics engine settings
  - `coulomb_constant`: Constant for Coulomb's law calculations (default: 0.8)
  - `min_distance`: Minimum distance between particles to prevent extreme forces (default: 0.001)
  - `min_velocity`: Minimum velocity magnitude to prevent division by zero (default: 0.001)
  - `large_force_threshold`: Threshold above which to warn about large forces (default: 10.0)

### Visualization Parameters
- `visualization`: Visualization settings
  - `colors`: Color codes for various elements
    - `background`: Background color of the 3D space (default: "#4B0082", INDIGO)
    - `positive`: Color for positive charge particles (default: "#FF0000", PURE_RED)
    - `negative`: Color for negative charge particles (default: "#0000FF", PURE_BLUE)
    - `tracer`: Color for path tracers when using single color (default: "#FFFFFF", WHITE)
    - `tracer_positive`: Color for positive charge particle tracers (default: "#FC6255", PALE_RED)
    - `tracer_negative`: Color for negative charge particle tracers (default: "#58C4DD", PALE_BLUE)
  - `marker_size`: Size of the particle markers (default: 0.04)
  - `use_dot3d`: Whether to use Dot3D instead of Sphere for particles (default: true)
  - `tracer`: Configuration for path tracers
    - `enabled`: Whether tracers are enabled (default: true)
    - `history_length`: Number of history points to display (default: 12000)
    - `stroke_width`: Width of the tracer lines (default: 1)
    - `fade`: Whether tracers should fade out over time (default: false)
    - `add_spheres`: Whether to add sphere markers along the trail (default: false)
    - `frames_between_trail_segments`: Number of frames between trail sphere markers (default: 60)
    - `sphere_radius`: Radius of the sphere markers (default: 0.02)
    - `max_sphere_radius`: Maximum radius for sphere markers (default: 0.1)
    - `use_particle_color`: Whether to use particle-specific tracer colors (default: true)
  - `scaling`: Configuration for auto-scaling
    - `enabled`: Whether auto-scaling is enabled (default: true)
    - `initial_scale`: Initial scale factor (default: 1.0)
    - `max_display_limit`: Maximum display limit for scaling down (default: 5.0)
    - `min_display_limit`: Minimum display limit for scaling up (default: 2.0)
    - `scale_stability_threshold`: Threshold for scale changes to apply smoothing (default: 0.2)
  - `sim_to_manim_ratio`: Ratio of simulation steps to animation frames (default: 5)
  - `manim_frame_rate`: Frame rate for the animation (default: 60)
  - `camera`: Camera configuration
    - `phi`: Phi angle for camera orientation in degrees (default: 75)
    - `theta`: Theta angle for camera orientation in degrees (default: 30)

## Physics Model

The default physics model uses a modified Coulomb's law with the following features:

- Opposite charges attract, like charges repel
- Forces are inversely proportional to the square of distance multiplied by particle velocity
- Minimum distance and velocity thresholds prevent extreme forces
- Support for multiple particles interacting simultaneously

## Visualization

The visualization uses Manim's 3D capabilities:

- Point potentials are shown as colored dots or spheres (red for positive, blue for negative)
- Path tracers show the history of each particle's movement
- Dynamic scaling adjusts the view to keep all particles visible
- Camera angles can be configured
- Option to add "dot tracers" showing particle positions at regular intervals

## Examples

### Simple Two-Particle System

```json
{
  "simulation": {
    "particles": [
      {
        "id": 1,
        "charge": 1,
        "position": [2.0, 0.0, 0.0],
        "velocity": [0.0, 0.5, 0.0]
      },
      {
        "id": 2,
        "charge": -1,
        "position": [-2.0, 0.0, 0.0],
        "velocity": [0.0, -0.5, 0.0]
      }
    ],
    "duration": 60
  }
}
```

## Development

### Adding New Action Functions

To create a new physics model:

1. Create a new file named `action_yourmodel.py`
2. Implement a class named `ActionYourmodel` with:
   - An `__init__` method that accepts a config parameter
   - An `apply` method that updates particle positions and velocities

### Extending the Visualization

The visualization system can be extended by:

1. Modifying `visualizer.py` to add new visual elements
2. Adding new configuration options to control visualization features
3. Creating custom Manim objects for specialized visualizations

## License

This project is available for use and modification according to the terms specified by the project owner.