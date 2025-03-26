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
- Camera movement uses Manim's `camera.frame.scale` method for smooth zooming
- Scale change per second is defined as: `scale_change = base_rate * 10^(abs(current_scale - target_scale)/duration)`
- Minimum zoom duration is 2 seconds even between adjacent scales
- Maximum zoom duration is 20 seconds for full-scale transitions

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
    "dot3d_radius": 0.04             // Point potential size
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

```python
import manim as m

# Base Scene class for common functionality
class ZoomableScene(m.Scene):
    def __init__(self, config, scale_value):
        super().__init__()
        self.config = config
        self.scale_value = scale_value
        self.objects = []
        self.scale_indicator = None
        self.background = None
        
    def setup(self):
        # Initialize scene components
        self.setup_background()
        self.setup_scale_indicator()
        
    def setup_background(self):
        # Creates background with config color
        self.background = m.Rectangle(
            width=config["global_settings"]["resolution"][0],
            height=config["global_settings"]["resolution"][1],
            fill_color=config["global_settings"]["background_color"],
            fill_opacity=1.0
        )
        self.add(self.background)
        
    def setup_scale_indicator(self):
        # Creates the 10^N scale indicator in top right
        scale_text = f"10^{self.scale_value}"
        self.scale_indicator = m.Text(
            scale_text,
            font_size=config["global_settings"]["font_size"],
            color=config["global_settings"]["color_text"]
        )
        # Position in top right corner with padding
        self.scale_indicator.to_corner(m.UR, buff=0.5)
        self.add(self.scale_indicator)
        
    def create_object(self, label, position, radius):
        # Creates a circle with label at position
        circle = m.Circle(
            radius=radius,
            stroke_color=config["global_settings"]["color_circle"],
            stroke_width=config["global_settings"]["stroke_width"],
            fill_opacity=0
        )
        circle.move_to(position)
        
        label_text = m.Text(
            label,
            font_size=config["global_settings"]["font_size"],
            color=config["global_settings"]["color_text"]
        )
        label_text.move_to(position)
        
        obj = m.VGroup(circle, label_text)
        self.objects.append(obj)
        self.add(obj)
        return obj
        
    def update_scale_indicator(self, new_scale):
        # Update scale indicator during transitions
        new_text = f"10^{new_scale:.1f}"
        new_indicator = m.Text(
            new_text,
            font_size=config["global_settings"]["font_size"],
            color=config["global_settings"]["color_text"]
        )
        new_indicator.to_corner(m.UR, buff=0.5)
        self.play(m.Transform(self.scale_indicator, new_indicator))

# Specific scene implementations
class UniverseScene(ZoomableScene):
    def construct(self):
        # Universe-specific initialization
        pass

# ... Additional scene classes ...

# Manager for zoom transitions
class ZoomManager:
    def __init__(self, json_config):
        self.config = self._load_config(json_config)
        self.scenes = self._initialize_scenes()
        self.current_scale = None
        self.current_scene = None
        self.animation_progress = 0
        self.total_duration = self._calculate_total_duration()
        self.audio_controller = AudioController(self.config.get("audio", {}))
        
    def _load_config(self, json_path):
        # Load and validate the JSON configuration
        import json
        with open(json_path, 'r') as f:
            config = json.load(f)
            
        # Validate required fields
        required_keys = ["global_settings", "scenes", "animation_sequence"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key in config: {key}")
                
        return config
        
    def _initialize_scenes(self):
        # Create all scene instances based on config
        scenes = {}
        for scene_config in self.config["scenes"]:
            scene_name = scene_config["name"]
            scale_value = scene_config["scale"]
            
            # Create appropriate scene class based on name
            if scene_name == "Universe":
                scene = UniverseScene(self.config, scale_value)
            elif scene_name == "GalaxyCluster":
                scene = GalaxyClusterScene(self.config, scale_value)
            # ... other scene types ...
            else:
                # Generic scene as fallback
                scene = ZoomableScene(self.config, scale_value)
                
            scenes[scene_name] = scene
            
        return scenes
        
    def _calculate_total_duration(self):
        # Calculate total animation duration including transitions and pauses
        total = 0
        for transition in self.config["animation_sequence"]:
            duration = transition.get("duration", 5)
            pause_before = transition.get("pause_before", 0)
            pause_after = transition.get("pause_after", 0)
            total += duration + pause_before + pause_after
        return total
        
    def _apply_easing(self, t, easing_type):
        # Apply easing function to create smoother animations
        if easing_type == "linear":
            return t
        elif easing_type == "smooth":
            # Smooth step function (3t² - 2t³)
            return 3 * t**2 - 2 * t**3
        elif easing_type == "accelerate":
            # Quadratic ease-in
            return t**2
        elif easing_type == "decelerate":
            # Quadratic ease-out
            return 1 - (1 - t)**2
        else:
            return t  # Default to linear
        
    def zoom_in(self, scene, target_scene, duration=None, easing="smooth"):
        # Handle zoom-in animation between scenes
        if duration is None:
            duration = self.config["global_settings"].get("default_transition_duration", 5)
            
        # Calculate the zoom rate based on scale difference
        start_scale = scene.scale_value
        end_scale = target_scene.scale_value
        scale_diff = abs(end_scale - start_scale)
        
        # Set up the animation
        def update_scale(t):
            # Apply easing and calculate current scale
            t_eased = self._apply_easing(t, easing)
            current_scale = start_scale - (t_eased * scale_diff)
            scene.update_scale_indicator(current_scale)
            
            # Calculate zoom factor
            zoom_factor = 10**(t_eased * scale_diff / 10)  # Divide by 10 to make it visually pleasing
            scene.camera.frame.scale(zoom_factor)
            
        # Run the animation with the update function
        scene.play(
            m.UpdateFromAlphaFunc(
                scene.camera.frame,
                lambda mob, alpha: update_scale(alpha)
            ),
            run_time=duration
        )
        
        # Transition to the target scene at the end
        scene.play(
            m.FadeOut(scene.background),
            m.FadeOut(*scene.objects),
            run_time=0.5
        )
        
        target_scene.play(
            m.FadeIn(target_scene.background),
            m.FadeIn(*target_scene.objects),
            run_time=0.5
        )
        
        self.current_scene = target_scene
        self.current_scale = end_scale
        
    def zoom_out(self, scene, target_scene, duration=None, easing="smooth"):
        # Similar to zoom_in but with inverse scaling
        # Essentially the same as zoom_in with start/end scales swapped
        if duration is None:
            duration = self.config["global_settings"].get("default_transition_duration", 5)
            
        # Calculate the zoom rate based on scale difference
        start_scale = scene.scale_value
        end_scale = target_scene.scale_value
        scale_diff = abs(end_scale - start_scale)
        
        # Set up the animation
        def update_scale(t):
            # Apply easing and calculate current scale
            t_eased = self._apply_easing(t, easing)
            current_scale = start_scale + (t_eased * scale_diff)
            scene.update_scale_indicator(current_scale)
            
            # Calculate zoom factor (inverse of zoom_in)
            zoom_factor = 1/(10**(t_eased * scale_diff / 10))
            scene.camera.frame.scale(zoom_factor)
            
        # Run the animation with the update function
        scene.play(
            m.UpdateFromAlphaFunc(
                scene.camera.frame, 
                lambda mob, alpha: update_scale(alpha)
            ),
            run_time=duration
        )
        
        # Transition to the target scene at the end
        scene.play(
            m.FadeOut(scene.background),
            m.FadeOut(*scene.objects),
            run_time=0.5
        )
        
        target_scene.play(
            m.FadeIn(target_scene.background),
            m.FadeIn(*target_scene.objects),
            run_time=0.5
        )
        
        self.current_scene = target_scene
        self.current_scale = end_scale
        
    def execute_animation_sequence(self):
        # Run the full animation sequence defined in config
        current_time = 0
        
        # Start audio if configured
        if self.config.get("audio", {}).get("background_music"):
            self.audio_controller.start_background_music()
        
        # Process each transition in the sequence
        for i, transition in enumerate(self.config["animation_sequence"]):
            from_scene_name = transition["from_scene"]
            to_scene_name = transition["to_scene"]
            direction = transition.get("direction", "in")
            duration = transition.get("duration", 5)
            easing = transition.get("easing_function", "smooth")
            pause_before = transition.get("pause_before", 0)
            pause_after = transition.get("pause_after", 0)
            
            from_scene = self.scenes[from_scene_name]
            to_scene = self.scenes[to_scene_name]
            
            # Initialize the first scene if this is the start
            if i == 0:
                self.current_scene = from_scene
                self.current_scale = from_scene.scale_value
                from_scene.setup()
                
            # Apply pause before if specified
            if pause_before > 0:
                self.current_scene.wait(pause_before)
                current_time += pause_before
                
                # Check for narration during pause
                self.audio_controller.check_narration_cues(current_time)
            
            # Execute the transition
            if direction == "in":
                self.zoom_in(from_scene, to_scene, duration, easing)
            else:  # "out"
                self.zoom_out(from_scene, to_scene, duration, easing)
                
            current_time += duration
            
            # Check for narration during transition
            self.audio_controller.check_narration_cues(current_time)
            
            # Apply pause after if specified
            if pause_after > 0:
                self.current_scene.wait(pause_after)
                current_time += pause_after
                
                # Check for narration during pause
                self.audio_controller.check_narration_cues(current_time)

# Audio handling for narration and background music
class AudioController:
    def __init__(self, audio_config):
        self.config = audio_config
        self.background_music = self.config.get("background_music")
        self.volume = self.config.get("volume", 0.5)
        self.narration_cues = self.config.get("narration_timings", [])
        self.narration_cues.sort(key=lambda x: x["timestamp"])
        self.current_narration_index = 0
        
    def start_background_music(self):
        if self.background_music:
            # Add background music using Manim's audio features
            # Implementation depends on Manim's audio capabilities
            pass
            
    def check_narration_cues(self, current_time):
        # Check if we need to play any narration cues at the current time
        while (self.current_narration_index < len(self.narration_cues) and 
               self.narration_cues[self.current_narration_index]["timestamp"] <= current_time):
            cue = self.narration_cues[self.current_narration_index]
            self._play_narration(cue["audio_file"], cue.get("volume", self.volume))
            self.current_narration_index += 1
            
    def _play_narration(self, audio_file, volume):
        # Play a narration audio file
        # Implementation depends on Manim's audio capabilities
        pass

# Main animation controller
class ZoomAnimation(m.Scene):
    def construct(self):
        config = "zoom_config.json"
        zoom_manager = ZoomManager(config)
        zoom_manager.execute_animation_sequence()
```

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
python zoom_animation.py [options]
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
# Render with default settings
python zoom_animation.py

# Render with custom configuration and output path
python zoom_animation.py --config custom_config.json --output universe_zoom.mp4

# Render in high quality with 4K resolution
python zoom_animation.py --quality high --resolution 3840x2160
```

## Future Enhancements

- Support for branching zoom paths (zoom into different objects at same scale)
- Interactive controls for user-directed zooming
- Enhanced visual effects during transitions between disparate scale levels
- Voiceover narration synchronized with visual transitions
- Export options for various video formats and resolutions
- Real-time display of physical constants and properties relevant to each scale
- Integration with external physics simulation data
- NPQG theory visualizations at appropriate scales
- Texture mapping and more detailed object representations
- Particle animation for the point potential scenes

## File Structure

```
zoom/
├── zoom_animation.py         # Main entry point
├── zoom_config.json          # Default configuration
├── scenes/                   # Scene implementations
│   ├── __init__.py
│   ├── base_scene.py         # ZoomableScene base class
│   ├── universe_scene.py     # UniverseScene implementation
│   ├── galaxy_scene.py       # GalaxyScene implementation
│   └── ...                   # Additional scene implementations
├── core/                     # Core functionality
│   ├── __init__.py
│   ├── zoom_manager.py       # ZoomManager implementation
│   ├── audio_controller.py   # Audio handling
│   └── config_loader.py      # Configuration parsing
├── assets/                   # Media assets
│   ├── audio/                # Background music and narration
│   │   ├── background.mp3
│   │   └── narration/
│   ├── textures/             # Textures for scene objects
│   └── data/                 # Scientific data for simulation
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── easing.py             # Animation easing functions
│   └── scale_converter.py    # Scale conversion utilities
└── examples/                 # Example configurations
    ├── simple_zoom.json
    ├── full_universe.json
    └── quantum_focus.json
```

## Dependencies and Performance Considerations

### Dependencies
- **Primary**: Python 3.8+, Manim Community Edition, NumPy
- **Audio**: ffmpeg-python, pydub
- **Optional**: SciPy (for complex physics calculations)

### Performance Optimization
- Pre-render complex scenes to texture maps for better performance
- Progressive loading of scene details based on zoom level
- GPU acceleration via Manim's OpenGL renderer
- Memory management for large-scale transitions

