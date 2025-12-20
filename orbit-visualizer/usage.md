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
- `fps` (int): Frames per second.
- `duration` (float): Minimum duration in seconds (coverage heuristic may extend).
- `field_speed` (float): Field propagation speed.
- `domain_half_extent` (float): Half extent of square domain, in world units.
- `coverage_margin` (float): Multiplier for auto-coverage duration.
- `max_memory_bytes` (int): Memory budget for cached frames (future use).
- `speed_multiplier` (float): Default path speed multiplier.
- `position_snap` (float): Optional XY snap grid size; ignored if `path_snap` is set.
- `path_snap` (float): Snap step in path parameter space (keeps positions on the path).
- `render` (bool): Start in render mode (PyGame).
- `field_visible` (bool): Show field texture by default.
- `start_paused` (bool): Start paused when rendering.
- `self_test` (bool): Print summary instead of normal output.
- `parallel_precompute` (bool): Toggle parallel precompute (reserved).
- `reverse` (bool): Default reverse flag for orbit (can be overridden per group).

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
  - `reverse` (bool): Reverse path orientation for the group.
  - `speed_multiplier` (float): Path speed multiplier override for the group.
  - `decay` (float): Spiral decay override (only for `exp_inward_spiral`).
- `simulation` (object): Reserved for future simulation rules (do not include with `orbit`).
