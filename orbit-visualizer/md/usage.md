# Run File Template

This describes every supported setting for JSON run files. Settings map to `directives` and `groups` fields in `circle.json` / `spiral.json`.

## Examples
From `orbit-visualizer`:
```
python orbits.py --run circle.json
python orbits.py --run spiral.json
python orbits.py --render --path unit_circle
```

From the repo root:
```
python orbit-visualizer/orbits.py --run orbit-visualizer/circle.json
python orbit-visualizer/orbits.py --run orbit-visualizer/spiral.json
python orbit-visualizer/orbits.py --render --path unit_circle
```

## Profiling
Built-in cProfile:
```
python -m cProfile -o /tmp/orbits.prof orbit-visualizer/orbits.py --run orbit-visualizer/circle.json
python - <<'PY'
import pstats
p = pstats.Stats("/tmp/orbits.prof")
p.sort_stats("cumtime").print_stats(30)
PY
```

Optional pyinstrument (if installed):
```
python -m pyinstrument -r text orbit-visualizer/orbits.py --run orbit-visualizer/circle.json
```

## Top-level structure
```
{
  "directives": { ... },
  "groups": [
    {
      "name": "...",
      "electrinos": 1,
      "positrinos": 1,
      "orbit": { ... }
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
- `domain_half_extent` (float): Half extent of square domain, in world units. (Legacy; use `world_size` instead.)
- `speed_multiplier` (float): Default path speed multiplier.
- `position_snap` (float): Optional XY snap grid size; ignored if `path_snap` is set.
- `path_snap` (float): Snap step in path parameter space (keeps positions on the path).
- `render` (bool): Start in render mode (PyGame).
- `field_visible` (bool): Show field texture by default.
- `start_paused` (bool): Start paused when rendering.
- `field_grid_scale_with_canvas` (bool): Scale field grid resolution by `canvas_scale`.
- `shell_thickness_scale_with_canvas` (bool): Multiply shell thickness by `1/canvas_scale`.
- `field_color_falloff` (string): `"inverse_r2"` for log10 mapping, `"inverse_r"` for sqrt log10 mapping.
- `shell_weight` (string): `"raised_cosine"` for smooth annular weights, `"hard"` for a flat band.
- `field_backend` (string): Preferred field update backend. Use one of:
  - `"gpu"`: GL instanced rings (requires `moderngl`).
  - `"cpu_incr"`: CPU incremental ring updates.
  - `"cpu_full"`: CPU full rebuild each frame.
  Legacy values are mapped automatically: `"gpu_instanced"` → `"gpu"`, `"cpu_incremental"` → `"cpu_incr"`, `"cpu_rebuild"` → `"cpu_full"`.
- `canvas_shrink` (float): Optional factor (default `0.9`) to reduce requested canvas size to avoid OS downscaling; set to `1.0` to request full size.
- `hi_dpi` (bool): Request a high-DPI window where supported (macOS Retina). Defaults to `false`.
- `seed_static_field` (bool): Pre-fill the field with stationary emissions for each architrino at startup. Defaults to `false`; enable only when you want a pre-baked field snapshot.
- `grid_visible` (bool): Show the 0.25x0.25 domain grid overlay. Defaults to `false`.

Aliases (optional):
- `field_on` → `field_visible`
- `snap_distance` → `position_snap`
- `path_step` → `path_snap`

## `groups` settings
Each group describes architrino counts and a motion block.

- `name` (string): Group label.
- `electrinos` (int): Number of electrinos (currently only `1` is supported).
- `positrinos` (int): Number of positrinos (currently only `1` is supported).
- `orbit` (object): Use a predefined path.
  - `path` (string): Path name (`unit_circle`, `exp_inward_spiral`).
  - `speed_multiplier` (float): Path speed multiplier override for the group.
  - `decay` (float): Spiral decay override (only for `exp_inward_spiral`).
- `simulation` (object): Reserved for future simulation rules (do not include with `orbit`).
  - `mover` (string, optional): Motion backend per architrino. Use `"analytic"` (default) for predefined paths, or `"physics"` (stubbed for future force-based motion).

### Per-arch settings (when you bypass `groups` and list `architrinos`)
- `name` (string): Architrino label.
- `polarity` (string): `"p"` or `"e"`.
- `mover` (string, optional): `"analytic"` or `"physics"`; required in `phases[0]` when phases are used.
- `path` (string, optional): Path name for analytic movers; required in `phases[0]` for analytic phases.
- `start_pos` (object): `{ "x": float, "y": float }`.
- `velocity` (object): `{ "speed": float, "heading_deg": float }` (heading is screen-friendly: 0=+x, 90=up).
- `phases` (array, required): Time-ordered behavior phases. The first phase must include `mover` (and `path` if analytic).
  - Each phase supports:
    - `mode` (string): `"frozen"` (hold position) or `"move"` (normal motion). Default `"move"`.
    - `duration_seconds` (float, optional): Length of this phase; if omitted, phase runs until the end of the list.
    - `speed_multiplier` (float, optional): Per-phase speed override (for both analytic and physics movers).
    - `mover` (string, optional): `"analytic"` or `"physics"` to switch mover in this phase.
    - `path` (string, optional): Target path for analytic phases (`unit_circle`, `exp_inward_spiral`).
    - `velocity` (object, optional): `{ "speed": float, "heading_deg": float }` override for physics movers during this phase.

Example architrino with a 10s warm-up, then motion:
```json
{
  "name": "p1",
  "polarity": "p",
  "mover": "physics",
  "start_pos": { "x": 1, "y": 1 },
  "velocity": { "speed": 0.5, "heading_deg": 90 },
  "phases": [
    { "mode": "frozen", "duration_seconds": 10 },
    { "mode": "move" }
  ]
}
```
