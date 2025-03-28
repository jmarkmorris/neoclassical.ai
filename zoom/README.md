# NPQG Universe Zoom Animation

This project creates a smooth zoom animation through different scales of the universe, from the largest observable universe down to the smallest subatomic particles.

## Animation Features

- Continuous zooming with smooth transitions
- Labels positioned to the right of each circle
- Dynamic scale indicator showing the current size
- Auto-dissolve effect when circles reach screen boundaries
- Full-sequence animation covering all scales

## How to Run

### Running the New Implementation

```bash
python updated_zoom.py
```

Options:
- `--quality` - Set quality (l=low, m=medium, h=high), default=m
- `--config` - Path to custom config file, default="zoom_config.json"
- `--output` - Custom output filename, default="zoom_animation.mp4"

Example:
```bash
python updated_zoom.py --quality h --output my_zoom.mp4
```

### Running the Original Implementation

```bash
python run_zoom.py
```

## Configuration

The animation is controlled by `zoom_config.json`, which defines:

- Scenes and their scale values
- Animation sequence and transitions
- Global visual settings (colors, durations, etc.)

## Output

The rendered animation will be saved to:
`./media/videos/updated_zoom/[quality]/ZoomAnimation.mp4`

## Notes

- The updated implementation provides labels next to circles
- Labels zoom with their circles for better context
- Dissolve effect when circles reach 95% of frame height
- Background is always visible outside of circles
