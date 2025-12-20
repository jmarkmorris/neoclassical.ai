# High-Level Design

## Overview
Render a 2-D timespace slice with predefined architrino trajectories, delayed circular emissions, and per-pixel superposition coloring. Scenarios are driven by JSON run files (`circle.json`, `spiral.json`) that declare directives and architrino groups. Live mode recomputes the field every frame from the retained emission history; pre-bake remains available for offline summaries.

## Core components
- **Scenario Loader**: Reads JSON run files with top-level `directives` and `groups`, producing the active simulation config and group orbits.
- **Trajectory Library**: Parameterized, piecewise-smooth paths in $(x,y,t)$ with direction-reversal option; supplies architrino positions per time step or snapped path parameters.
- **Field Engine**: Computes per-pixel scalar potential from delayed shells (radius $r = v\,\tau$, magnitude $1/r^2$) for each emission event; field is rebuilt each frame from the retained emission list.
- **Renderer**: Maps field values to RGB (red/blue superposition, purple at neutrality) and draws overlays (architrino markers, emitter markers, causal shells, retarded lines, hit connectors).
- **Hit Detector**: Finds causal roots satisfying $\|\mathbf{s}_r(t) - \mathbf{s}_e(t_0)\| = v\,(t - t_0)$; records hit strength ($\propto 1/r^2$) and angle $\theta \in [0,2\pi)$; colors hit entries by emitter polarity.
- **UI Layer**: Layout with dominant visualization pane and control strip for start/restart/pause, scrub, speed multipliers, overlay toggles, scaling mode, and path selection.
- **Playback/Export**: Plays live-computed frames or pre-baked frames; exports image stacks or video via ffmpeg/imageio.

## Data flow (pre-baked mode)
1) Select path, speed profile, and resolution (via run file).  
2) Trajectory Library emits $(\mathbf{s}(t), \mathbf{v}(t))$ samples.  
3) Field Engine computes per-frame field textures; Hit Detector logs hits.  
4) Frames (RGB) + hit tables serialized to disk (or RAM cache).  
5) Renderer/UI loads frames for smooth playback and scrubbing; overlays hit info and markers.  

## Data flow (live mode)
1) Load run file, build scenario config and primary orbit.  
2) Per-frame: Trajectory Library -> Field Engine (rebuild from emissions) -> Hit Detector.  
3) Renderer composites field + overlays; UI events adjust speed/pause/field toggle in real time.  

## Run file structure
Run files define `directives` and `groups`.
- `directives`: global settings (hz, field speed, snaps, render flags).
- `groups`: array of architrino groups; each group declares counts and either `orbit` or `simulation`.
- Current limit: one group with 1 electrino + 1 positrino; simulation rules are reserved for future scenarios.

## Path history granularity
- **Temporal cadence**: one emission per architrino per frame (`dt = 1 / hz`).
- **Retention window**: emissions older than `max_radius / field_speed` are dropped; `max_radius` depends on `domain_half_extent`.
- **Path snapping**: `path_snap` quantizes the path parameter (keeps positions on the path).
- **Position snapping**: `position_snap` quantizes XY positions only when `path_snap` is unset.

## Field calculation details
Each frame clears the field grid and re-applies every retained emission as an annular band at radius `r = field_speed * (t - t_emit)`. Contributions are signed by polarity and summed into the grid, then mapped to RGB for display.

## Performance tiers
- **CPU Tier**: NumPy + Numba for field and hit computation; PyGame/pyglet for rendering and UI; optional pre-bake for smooth playback.
- **GPU Tier**: ModernGL + GLSL for per-pixel shading when immediate, no-bake updates are required; CPU mirrors hit detection for logging/table outputs.

## Extensibility
- Add new paths, speed profiles, or additional architrinos by extending the Trajectory Library.
- Introduce alternative color maps or scaling functions in the Field Engine.
- Swap playback backend (e.g., browser canvas/WebGL) while reusing the same pre-baked assets and logs.
