# NPQG Universe Zoom Animation

## Project Overview
A visualization tool that animates zooming across all scales of the universe, from cosmological to sub-atomic levels, using Python and Manim. The animation seamlessly transitions between hierarchical scenes, enabling exploration from the universe scale down to point potentials at the quantum level.

### Project Goals
1. Create a scientifically accurate representation of objects across all scales of the universe
2. Demonstrate the conceptual framework of NPQG (Neoclassical Physics and Quantum Gravity) theory
3. Visualize the transition between classical and quantum scales
4. Provide an educational tool showing the relative scales of cosmic and subatomic structures
5. Illustrate the point potential architecture outlined at neoclassical.ai

### Prerequisites
- Python 3.8+
- Manim Community Edition v0.17.2+
- NumPy and SciPy for mathematical calculations
- FFmpeg for video rendering
- JSON library for configuration file parsing

## Technical Architecture

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

### Scene Design Specifications

#### Visual Elements
- **Canvas**: Manim frame with origin at center, dimensions 1920x1080 pixels
- **Background**: INDIGO (#4B0082)
- **Objects**: Represented as white circular outlines with no fill, stroke width of 2 pixels
- **Labels**: Centered text within each object, displaying the object name with font size 24pt and white color
- **Scale Indicator**: Logarithmic scale (10^N format) displayed in top right corner, updating dynamically
- **Font**: DejaVu Sans for consistent display across platforms
- **Frame Rate**: 60 FPS for smooth transitions

#### Object Representation
- Single objects are centered in the frame
- Multiple objects at same scale level are distributed within the parent object's circle
- Point potentials at the deepest zoom level use Dot3D:
  - Positive potentials: PURE_RED with radius 0.04
  - Negative potentials: PURE_BLUE with radius 0.04

### Animation Mechanics

#### Zoom Implementation
- **ZoomManager Class**: Controls all zoom operations
  - `zoom_in(scene, target_scene)`: Transitions from current to more detailed scene
  - `zoom_out(scene, target_scene)`: Transitions from current to less detailed scene
  - Manages the scaling rate and scene transitions
  - Updates the logarithmic scale indicator dynamically

#### Zoom Behavior
- Circles expand beyond frame boundaries during zoom-in
- Circles contract from outside frame during zoom-out
- Default zoom rate is constant logarithmically (configurable)
- Transition blending between consecutive scenes for seamless animation
- Scaling and opacity transitions for smooth scene changes
- Scale indicator updates dynamically during transitions
- Scene elements are designed to blend seamlessly during transitions
- Labels move from inside circles to the top left corner during transitions

### Configuration System

#### JSON Input Schema
```json
{
  "global_settings": {
    "default_zoom_rate": 0.5,        // Logarithmic zoom rate
    "background_color": "#4B0082",   // Indigo background
    "scale_range": [-60, 60],        // Min/max logarithmic scale values
    "resolution": [1920, 1080],      // Width x Height in pixels
    "frame_rate": 60,                // Frames per second
    "font_size": 24,                 // Default text size
    "stroke_width": 2,               // Width of circle outlines
    "color_text": "#FFFFFF",         // White text
    "color_circle": "#FFFFFF",       // White circles
    "dot3d_radius": 0.04,            // Point potential size
    "quality": "h"                   // Rendering quality (l=low, m=medium, h=high)
  },
  "scenes": [
    {
      "name": "Universe",
      "scale": 26,             // 10^26
      "objects": [
        {
          "label": "Observable Universe",
          "position": [0, 0, 0],
          "radius": 3
        }
      ],
      "zoom_rate_override": null  // Use default rate if null
    },
    // Additional scenes...
  ],
  "animation_sequence": [
    {
      "from_scene": "Universe",
      "to_scene": "GalaxyCluster",
      "direction": "in",
      "duration": 5,                   // In seconds
      "easing_function": "smooth",     // Animation easing (smooth, linear, accelerate, decelerate)
      "pause_before": 1,               // Pause before starting transition (seconds)
      "pause_after": 1,                // Pause after completing transition (seconds)
      "scale_indicator_visible": true  // Whether to show the scale indicator during this transition
    },
    // Additional transitions...
  ],
  "audio": {
    "background_music": "path/to/background.mp3",   // Optional background audio
    "volume": 0.5,                                  // 0.0 to 1.0
    "narration_timings": [                          // Optional narration cues
      {
        "timestamp": 3.5,                           // Seconds from start
        "audio_file": "path/to/narration1.mp3",
        "duration": 2.8
      }
    ]
  }
}
```

### Implementation Classes

The implementation follows a modular architecture with the following key components:

- **ZoomableScene**: Base class for all scene types
  - Manages common elements like scale indicators and backgrounds
  - Provides methods for creating and updating scene elements

- **Specific Scene Classes**: (UniverseScene, GalaxyScene, etc.)
  - Extend ZoomableScene with scale-specific visualizations
  - Implement get_elements() to create detailed scene representations
  - Handle custom physics and visual effects relevant to each scale

- **ZoomManager**: Manages transitions between scenes
  - Controls zoom animations and timing
  - Maintains the current scale value during transitions
  - Handles scene blending for seamless transitions
  - Displays transition labels to indicate current operation

- **AudioController**: Handles audio elements 
  - Manages background music
  - Provides narration cues at appropriate timestamps

- **ConfigLoader**: Processes the configuration file
  - Validates configuration data
  - Provides defaults for missing values
  - Converts configuration into appropriate objects

## Execution Process

1. Parse the JSON configuration file
2. Initialize all scene objects with their respective configurations
3. Create the ZoomManager with the parsed configuration
4. Execute the animation sequence, controlling transitions between scenes
5. Dynamically update the scale indicator during zoom operations
6. Process audio cues and narration synchronized with visual elements
7. Render the final animation with proper scene blending for seamless transitions

## Command Line Interface

The animation can be executed through a command-line interface:

```bash
python run_zoom.py [options]
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
# Render with default settings (high quality)
python run_zoom.py

# Render with custom configuration
python run_zoom.py --config custom_config.json

# Render in low quality for faster preview
python run_zoom.py --quality l

# Render to a file without preview
python run_zoom.py --no-preview --output universe_zoom.mp4

# Run in simple mode (faster, less detailed)
python run_zoom.py --mode simple
```

## Full Zoom Capabilities

The current implementation includes all 11 scales:

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

The animation provides a complete journey through all scales, with smooth transitions between each scale level, both zooming in and zooming out.

## Future Enhancements

- Support for branching zoom paths (zoom into different objects at same scale)
- Interactive controls for user-directed zooming
- Enhanced visual effects during transitions between disparate scale levels
- Voiceover narration synchronized with visual transitions
- Export options for various video formats and resolutions
- Real-time display of physical constants and properties relevant to each scale
- Integration with external physics simulation data
- NPQG theory visualizations at appropriate scales
- More detailed object representations with improved texturing
- Particle animation for the point potential scenes

## File Structure

```
zoom/
├── zoom_animation.py         # Main entry point
├── run_zoom.py               # Command-line interface
├── simple_zoom.py            # Simplified version for troubleshooting
├── zoom_config.json          # Default configuration
├── scenes/                   # Scene implementations
│   ├── base_scene.py         # ZoomableScene base class
│   ├── universe_scene.py     # UniverseScene implementation
│   ├── galaxy_cluster_scene.py # GalaxyClusterScene implementation
│   ├── galaxy_scene.py       # GalaxyScene implementation
│   ├── black_hole_scene.py   # BlackHoleScene implementation
│   ├── solar_system_scene.py # SolarSystemScene implementation
│   ├── star_scene.py         # StarScene implementation
│   ├── molecule_scene.py     # MoleculeScene implementation
│   ├── atom_scene.py         # AtomScene implementation
│   ├── electron_scene.py     # ElectronScene implementation
│   ├── quark_scene.py        # QuarkScene implementation
│   └── point_potential_scene.py # PointPotentialScene implementation
├── core/                     # Core functionality
│   ├── zoom_manager.py       # ZoomManager implementation
│   ├── audio_controller.py   # Audio handling
│   └── config_loader.py      # Configuration parsing
├── assets/                   # Media assets
│   ├── audio/                # Background music and narration
│   │   ├── background.mp3
│   │   └── narration/
│   └── textures/             # Textures for scene objects
├── utils/                    # Utility functions
│   ├── easing.py             # Animation easing functions
│   └── scale_converter.py    # Scale conversion utilities
└── examples/                 # Example configurations
    └── simple_zoom.json
```

## Dependencies and Performance Considerations

### Dependencies
- **Primary**: Python 3.8+, Manim Community Edition, NumPy
- **Audio**: ffmpeg-python, pydub
- **Optional**: SciPy (for complex physics calculations)

### Performance Optimization
- Pre-render complex scenes to texture maps for better performance
- Progressive loading of scene details based on zoom level
- Separating animations into sequential steps for better Manim compatibility
- Memory management for large-scale transitions
- High-quality rendering option for final output