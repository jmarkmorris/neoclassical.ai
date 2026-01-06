# Run File Template

This describes every supported setting for JSON run files. Settings map to `directives` and `architrinos` fields in the json files.

## Examples
From `sim2`:
```
python orbits.py --run json/circle.json
python orbits.py --run json/spiral-inv_r2.json
```

From the repo root:
```
python sim2/orbits.py --run sim2/json/circle.json
python sim2/orbits.py --run sim2/json/spiral-inv_r2.json
```

## Profiling
Built-in cProfile:
```
python -m cProfile -o /tmp/orbits.prof sim2/orbits.py --run sim2/circle.json
python - <<'PY'
import pstats
p = pstats.Stats("/tmp/orbits.prof")
p.sort_stats("cumtime").print_stats(30)
PY
```

Optional pyinstrument (if installed):
```
python -m pyinstrument -r text sim2/orbits.py --run sim2/circle.json
```

## Top-level structure
```
{
  "directives": { ... },
  "architrinos": [
    {
      "name": "p1",
      "polarity": "p",
      "start_pos": { "x": 1.0, "y": 0.0 },
      "velocity": { "speed": 0.5, "heading_deg": 90 },
      "phases": [
        { "mode": "move", "mover": "analytic", "path": "unit_circle" }
      ]
    }
  ]
}
```

## `directives` settings
- `format_version` (int): Version marker for future migrations.
- `hz` (int): Simulation frequency in Hz.
- `field_speed` (float): Field propagation speed.
- `max_force` (float): Clamp for physics impulse magnitude (prevents blow-ups).
- `world_size` (float): Full width/height of the square world domain in world units. (Preferred.)
- `domain_half_extent` (float): Half extent of square domain, in world units (use instead of `world_size` if you want half-size directly).
- `speed_multiplier` (float): Default path speed multiplier.
- `position_snap` (float): Optional XY snap grid size; ignored if `path_snap` is set.
- `path_snap` (float): Snap step in path parameter space (keeps positions on the path).
- `render` (bool): Start in render mode (PyGame).
- `field_visible` (bool): Show field texture by default.
- `start_paused` (bool): Start paused when rendering.
- `field_grid_scale_with_canvas` (bool): Scale field grid resolution by `canvas_scale`.
- `shell_thickness_scale_with_canvas` (bool): Multiply shell thickness by `1/canvas_scale`.
- `field_color_falloff` (string): Options for shading the field intensity.
  - `"inverse_r2"` for log10 mapping. 
  - `"inverse_r"` for sqrt log10 mapping. 
  - `"linear"` for direct linear mapping with a fixed clamp based on the most recent emission shell.
- `shell_weight` (string): 
  - `"raised_cosine"` for smooth annular weights. 
  - `"hard"` for a flat band.
- `field_alg` (string): Preferred field update backend. Use one of:
  - `"gpu"`: GL instanced rings (requires `moderngl`).
  - `"cpu_incr"`: CPU incremental ring updates.
  - `"cpu_full"`: CPU full rebuild each frame.
- `canvas_shrink` (float): Optional factor (default `0.9`) to reduce requested canvas size to avoid OS downscaling; set to `1.0` to request full size.
- `seed_static_field` (bool): Pre-fill the field with stationary emissions for each architrino at startup. Defaults to `false`; enable only when you want a pre-baked field snapshot.
- `grid_visible` (bool): Show the 0.25x0.25 domain grid overlay. Defaults to `false`.

## `architrinos` settings
Each entry describes one architrino.

- `name` (string): Architrino label.
- `polarity` (string): `"p"` or `"e"`.
- `start_pos` (object): `{ "x": float, "y": float }`.
- `velocity` (object): `{ "speed": float, "heading_deg": float }` (heading is screen-friendly: 0=+x, 90=up).
- `path` (string, optional): Default path for analytic phases (`unit_circle`, `exp_inward_spiral`).
- `decay` (float, optional): Spiral decay override (only for `exp_inward_spiral`).
- `phases` (array, required): Time-ordered behavior phases. `phases[0].mover` is required; analytic movers need a path in `phases[0]` or `path` above.
  - Each phase supports:
    - `mode` (string): `"frozen"` (hold position) or `"move"` (normal motion). Default `"move"`.
    - `duration_seconds` (float, optional): Length of this phase; if omitted, phase runs until the end of the list.
    - `speed_multiplier` (float, optional): Per-phase speed override (for both analytic and physics movers).
    - `mover` (string, required in `phases[0]`): `"analytic"` or `"physics"`.
    - `path` (string, optional): Target path for analytic phases (`unit_circle`, `exp_inward_spiral`).
    - `velocity` (object, optional): `{ "speed": float, "heading_deg": float }` override for physics movers during this phase.

Example architrino with a 10s warm-up, then motion:
```json
{
  "name": "p1",
  "polarity": "p",
  "start_pos": {
    "x": 1.0,
    "y": 1.0
  },
  "velocity": {
    "speed": 0.5,
    "heading_deg": 90
  },
  "phases": [
    {
      "mode": "frozen",
      "duration_seconds": 10,
      "mover": "physics"
    },
    {
      "mode": "move",
      "mover": "physics"
    }
  ]
}
```
