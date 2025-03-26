# NPQG Universe Zoom Animation

A visualization tool that animates zooming across all scales of the universe, from cosmological to sub-atomic levels, using Python and Manim. The animation seamlessly transitions between hierarchical scenes, enabling exploration from the universe scale down to point potentials at the quantum level.

## Overview

This project creates an interactive zoom animation that visualizes the relative scales of cosmic and subatomic structures, demonstrating the conceptual framework of NPQG (Nature's Fundamental Particle-based Quantum Gravity) theory.

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
   cd NPQG/zoom
   ```

2. Install dependencies:
   ```
   pip install manim numpy scipy
   ```

3. Ensure FFmpeg is installed on your system. If not, install it using your package manager.

## Usage

### Basic Usage

Run the animation with default settings:

```bash
python zoom_animation.py
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to the JSON configuration file (default: zoom_config.json) |
| `--output PATH` | Output video file path (default: zoom_animation.mp4) |
| `--quality {low,medium,high}` | Rendering quality preset (default: medium) |
| `--resolution WIDTHxHEIGHT` | Output resolution (default: 1920x1080) |
| `--frame-rate FPS` | Frame rate in FPS (default: 60) |
| `--preview` | Show animation preview instead of rendering |
| `--verbose` | Show detailed progress information |

### Example Usage

```bash
# Render with custom configuration and output path
python zoom_animation.py --config examples/simple_zoom.json --output universe_zoom.mp4

# Render in high quality with 4K resolution
python zoom_animation.py --quality high --resolution 3840x2160

# Preview the animation without rendering to a file
python zoom_animation.py --preview
```

## Configuration

The animation is configured using a JSON file that defines the scenes, objects, and zoom behavior.

### Example Configuration

```json
{
  "global_settings": {
    "default_zoom_rate": 0.5,
    "background_color": "#4B0082",
    "scale_range": [-60, 60],
    "resolution": [1920, 1080],
    "frame_rate": 60,
    "font_size": 24,
    "stroke_width": 2,
    "color_text": "#FFFFFF",
    "color_circle": "#FFFFFF",
    "dot3d_radius": 0.04
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
      ],
      "zoom_rate_override": null
    },
    ...
  ],
  "animation_sequence": [
    {
      "from_scene": "Universe",
      "to_scene": "GalaxyCluster",
      "direction": "in",
      "duration": 5,
      "easing_function": "smooth",
      "pause_before": 1,
      "pause_after": 1,
      "scale_indicator_visible": true
    },
    ...
  ],
  "audio": {
    "background_music": "assets/audio/background.mp3",
    "volume": 0.5,
    "narration_timings": [
      {
        "timestamp": 1.0,
        "audio_file": "assets/audio/narration/intro.mp3",
        "duration": 2.0
      },
      ...
    ]
  }
}
```

### Scene Hierarchy

The animation is structured as a hierarchy of scenes, each representing a specific scale:

| Scene Level | Scale (approx.) | Description |
|-------------|-----------------|-------------|
| UniverseScene | 10^26 m | Observable universe |
| GalaxyClusterScene | 10^23 m | Galaxy clusters and superclusters |
| GalaxyScene | 10^21 m | Individual galaxies |
| BlackHoleScene | 10^12 m | Supermassive black holes |
| SolarSystemScene | 10^11 m | Star systems with planets |
| StarScene | 10^9 m | Individual stars |
| MoleculeScene | 10^-8 m | Molecular structures |
| AtomScene | 10^-10 m | Atomic structures |
| ElectronScene | 10^-15 m | Electron scale |
| QuarkScene | 10^-18 m | Quark structures within hadrons |
| PointPotentialScene | 10^-60 m | Neoclassical point potentials |

## Adding New Scenes

To add a new scene type:

1. Create a new scene class in the `scenes` directory, inheriting from `ZoomableScene`
2. Implement the `construct` method to define the scene's visual elements
3. Add the scene to the configuration file
4. Update the scene initialization in `zoom_manager.py`

## License

This project is licensed under the [LICENSE] - see the LICENSE file for details.

## Acknowledgements

- [Manim Community](https://www.manim.community/) for the animation framework
- NPQG theory visualizations at [neoclassical.ai](https://neoclassical.ai)