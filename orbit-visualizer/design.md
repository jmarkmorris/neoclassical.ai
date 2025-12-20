# High-Level Design

## Overview
Render a 2-D timespace slice with predefined architrino trajectories, delayed circular emissions, and per-pixel superposition coloring. Scenarios are driven by JSON run files (`circle.json`, `spiral.json`) that declare directives and architrino groups. Live mode recomputes the field every frame from the retained emission history.

## Core components
- **Scenario Loader**: Reads JSON run files with top-level `directives` and `groups`, producing the active simulation config and group orbits.
- **Trajectory Library**: Parameterized, piecewise-smooth paths in $(x,y,t)$; supplies architrino positions per time step or snapped path parameters.
- **Field Engine**: Computes per-pixel scalar potential from delayed shells (radius $r = v\,\tau$, magnitude $1/r^2$) for each emission event; field is rebuilt each frame from the retained emission list.
- **Renderer**: Maps field values to RGB (red/blue superposition, purple at neutrality) and draws overlays (architrino markers, emitter markers, causal shells, retarded lines, hit connectors).
- **Hit Detector**: Finds causal roots satisfying $\|\mathbf{r}_r(t) - \mathbf{r}_e(t_0)\| = v\,(t - t_0)$; records hit strength ($\propto 1/r^2$) and emitter polarity.
- **UI Layer**: Layout with dominant visualization pane and control strip for start/restart/pause, scrub, speed multipliers, overlay toggles, scaling mode, and path selection.
- **Playback/Export**: Plays live-computed frames; export hooks are future work.

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

## Path history, hits, and field data structures
### Path history sampling and storage
- **Simulation cadence**: fixed timestep `dt = 1 / hz`. Each step advances the path parameter and snapshots positions for all architrinos.
- **Path snapping**: when `path_snap` is set, the path parameter is quantized (`round(param / path_snap) * path_snap`), ensuring samples remain on the analytic path. If `path_snap` is unset, `position_snap` can quantize XY positions.
- **Trace buffer**: path traces are stored as recent position lists per architrino (`path_traces[name]`). The list is append-only during playback and trimmed to `trace_limit` to avoid unbounded growth.

### Emission history
- **Emission cadence**: each architrino emits once per simulation step, producing an `Emission(time, pos, emitter)` entry.
- **Retention window**: emissions older than `max_radius / field_speed` are discarded (`max_radius ≈ sqrt(2) * domain_half_extent * 1.1`). This bounds memory use and the per-frame field rebuild cost.
- **Storage**: emissions are stored in a list; pruning runs every simulation step.

### Hit detection
- **Source of truth**: hits are derived strictly from emission history (no analytic root solving).
- **Causal condition**: for each emission with age `tau = t - t_emit`, the shell radius is `r = field_speed * tau`. A hit occurs when `|distance(receiver, emission.pos) - r| <= tolerance`.
- **Tolerance**: `tolerance` scales with `dt` to avoid missing hits under discrete stepping.
- **Self hits**: allowed only when `speed_multiplier > field_speed`; they are detected with the same emission-history loop.
- **De-duplication**: a `(t_emit, emitter, receiver)` key avoids repeated hits across frames.

### Field rendering
- **Per-frame rebuild**: the field grid is reset each frame and reconstructed from retained emissions.
- **Shell contribution**: for each emission, an annular band is added where `|dist - r| <= band_half`; contribution is `sign / dist^2` with a raised-cosine radial weight.
- **Polarity**: positrino contributions are positive, electrino contributions negative.
- **Color map**: the signed field is scaled by the 99th percentile magnitude and mapped to RGB (`red` for negative, `blue` for positive, green for near-neutral).

## Performance tiers
- **CPU Tier**: NumPy + Numba for field and hit computation; PyGame/pyglet for rendering and UI; optional pre-bake for smooth playback.
- **GPU Tier**: ModernGL + GLSL for per-pixel shading when immediate, no-bake updates are required; CPU mirrors hit detection for logging/table outputs.

## Extensibility
- Add new paths, speed profiles, or additional architrinos by extending the Trajectory Library.
- Introduce alternative color maps or scaling functions in the Field Engine.
- Swap playback backend (e.g., browser canvas/WebGL) while reusing the same pre-baked assets and logs.
