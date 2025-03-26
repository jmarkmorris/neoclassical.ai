# NPQG Universe Zoom Animation

A visualization tool that animates zooming across all scales of the universe, from cosmological to sub-atomic levels, using Python and Manim. The animation seamlessly transitions between hierarchical scenes, enabling exploration from the universe scale (10^26 m) down to point potentials at the quantum level (10^-60 m).

## Overview

This project creates an interactive zoom animation that visualizes the relative scales of cosmic and subatomic structures, demonstrating the conceptual framework of NPQG (Nature's Fundamental Particle-based Quantum Gravity) theory. It now features all 11 scale levels with detailed visualizations at each scale.

## Prerequisites

- Python 3.8+
- Manim Community Edition v0.17.2+
- NumPy and SciPy for mathematical calculations
- FFmpeg for video rendering
- JSON library for configuration file parsing

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd neoclassical.ai/zoom
   ```

2. Install dependencies:
   ```
   pip install manim numpy scipy
   ```

3. Ensure FFmpeg is installed on your system. If not, install it using your package manager.

## Usage

### Basic Usage

Run the animation with default settings (high quality):

```bash
python run_zoom.py
```

### Running the Full Zoom Animation

To run the complete zoom animation from the largest scale (Universe) to the smallest (Point Potential) and back:

```bash
python run_zoom.py --mode full
```

This will use the default configuration in `zoom_config.json`, which includes all 11 scale levels and transitions between them.

### Quick Preview

For faster rendering during development:

```bash
python run_zoom.py --quality l
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to the JSON configuration file (default: zoom_config.json) |
| `--quality {l,m,h}` | Rendering quality preset (l=low, m=medium, h=high) (default: h) |
| `--no-preview` | Disable preview mode (render to file) |
| `--output PATH` | Output video file path (default: zoom_animation.mp4) |
| `--mode {full,simple}` | Animation mode: full architecture or simple version |

### Example Usage

```bash
# Render with custom configuration
python run_zoom.py --config custom_config.json

# Render in low quality for faster preview
python run_zoom.py --quality l

# Render to a file without preview
python run_zoom.py --no-preview --output universe_zoom.mp4

# Run in simple mode (faster, less detailed)
python run_zoom.py --mode simple
```

## Implemented Scenes

The animation includes the following scale levels:

1. **Universe** (10^26 m)
2. **Galaxy Cluster** (10^23 m)
3. **Galaxy** (10^21 m)
4. **Black Hole** (10^12 m)
5. **Solar System** (10^11 m)
6. **Star** (10^9 m)
7. **Molecule** (10^-8 m)
8. **Atom** (10^-10 m)
9. **Electron** (10^-15 m)
10. **Quark** (10^-18 m)
11. **Point Potential** (10^-60 m)

Each scene includes detailed visualizations appropriate to its scale, with smooth transitions between adjacent scales.

## Scene Details

1. **UniverseScene**: Observable universe (10^26 m)
   - Cosmic microwave background visualization
   - Galaxy cluster distribution

2. **GalaxyClusterScene**: Galaxy cluster (10^23 m)
   - Multiple galaxy types (spiral, elliptical, irregular)
   - Intergalactic medium representation

3. **GalaxyScene**: Galaxy (10^21 m)
   - Spiral arms with star distributions
   - Central galactic bulge
   - Dark matter halo

4. **BlackHoleScene**: Black hole (10^12 m)
   - Event horizon and accretion disk
   - Relativistic jets
   - Gravitational lensing effects

5. **SolarSystemScene**: Solar system (10^11 m)
   - Star at center
   - Orbiting planets (with varying sizes and colors)
   - Asteroid belt
   - Outer solar system objects

6. **StarScene**: Star (10^9 m)
   - Core, radiation zone, convection zone
   - Surface granulation
   - Solar flares and prominences
   - Corona

7. **MoleculeScene**: Molecular scale (10^-8 m)
   - DNA double helix structure
   - Protein molecule (alpha helix)
   - Water molecules

8. **AtomScene**: Atomic scale (10^-10 m)
   - Nucleus with protons and neutrons
   - Electron orbitals
   - Orbital probability clouds

9. **ElectronScene**: Electron scale (10^-15 m)
   - Electron quantum field
   - Quantum fluctuations
   - Electron-positron pairs

10. **QuarkScene**: Quark scale (10^-18 m)
    - Proton structure with three quarks
    - Gluon field
    - Strong force visualization

11. **PointPotentialScene**: Point potential scale (10^-60 m)
    - Quantum foam
    - Wavefunction visualization
    - Spacetime curvature

## Configuration

The animation is configured using a JSON file that defines scenes, objects, and zoom behavior. The default configuration in `zoom_config.json` includes all scales and a complete sequence of zoom transitions.

### Key Configuration Elements

```json
{
  "global_settings": {
    "default_zoom_rate": 0.5,
    "background_color": "#4B0082",
    "scale_range": [-60, 60],
    "quality": "h"
  },
  "scenes": [
    {
      "name": "Universe",
      "scale": 26,
      "objects": [
        {
          "label": "Observable Universe",
          "position": [0, 0, 0],
          "radius": 3
        }
      ]
    },
    ...
  ],
  "animation_sequence": [
    {
      "from_scene": "Universe",
      "to_scene": "GalaxyCluster",
      "direction": "in",
      "duration": 4,
      "easing_function": "smooth",
      "pause_before": 2,
      "pause_after": 1
    },
    ...
  ]
}
```

## Adding New Scenes

To add a new scene type:

1. Create a new scene class in the `scenes` directory, inheriting from `ZoomableScene`
2. Implement the `get_elements()` method to create the scene's visual elements
3. Add the scene to the configuration file
4. Update the scene initialization in `zoom_manager.py`

## License

This project is licensed under the [LICENSE] - see the LICENSE file for details.

## Acknowledgements

- [Manim Community](https://www.manim.community/) for the animation framework
- NPQG theory visualizations at [neoclassical.ai](https://neoclassical.ai)