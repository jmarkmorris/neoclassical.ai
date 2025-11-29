# Project
Build a continuously animated 2-D dynamical geometry visualizer for orbiting partner charges, showing per-pixel field computations plus geometric overlays (orbits, retarded-position lines, causal shells) with interactive playback and exportable frames.

# Requirements
## Layout and UI
- Visualization pane occupies the majority of the viewport; controls and hit table live on the left, outside the canvas.
- Controls include start/restart, pause, scrub, speed multipliers, FPS selector (default 30 fps, adjustable lower if needed), and visualization toggles (e.g., delayed potential display, scaling mode).
- Default spatial scale: 4K canvas mapped to a symmetric square domain (e.g., [-2, 2] × [-2, 2]), giving ~0.001 units per pixel; adjust dynamically if zooming is added.

## Kinematics and paths
- Dimensionless 2-D spatial slice $(x,y)$ with absolute time $t$; field speed is fixed to $v=1$.
- Initial positions at $t=0$: electrino at $(-1, 0)$, positrino at $(1, 0)$; default worldlines are the unit circle with a $\pi$ phase separation.
- Trajectories are predefined, piecewise-smooth curves parameterized by $t$; the user selects from a library with an option to reverse path orientation. Path library (stub): unit circle (default) and exponential inward spirals; more to be added later.
- Changing the orbit/path definition or reversing orientation triggers a full restart; other controls either resume from pause or restart as appropriate.
- Motion follows the selected trajectory; no force-based integration is performed at this stage.
- Future extensibility: support new orbits/paths and varying the number of architrinos.

## Field emission and visualization
- Maintain interactive animation (target 30–60 fps) with per-pixel scalar/vector field evaluation over time.
- Each architrino emits potential shells at constant cadence and amplitude; shells expand as circles with radius $r = v\,\tau$.
- Potential magnitude follows $1/r^2$ on the shell; the visualization shows the planar cross-section via per-pixel color.
- Delayed-potential overlay can be toggled live without pausing.
- Architrino markers: electrino as a small pure-blue circle (RGB 0,0,255), positrino as a small pure-red circle (RGB 255,0,0); emitter markers are visually distinct (e.g., baby blue for electrino emitters, pink for positrino emitters).
- Field color equals the per-pixel superposition of red and blue contributions; neutral potential ($0$) renders as pure purple.
- Non-neutral pixels shade proportionally to net superposition with linear scaling initially; logarithmic scaling is deferred (future toggle).
- Draw orbits, rays/retarded lines, causal shells, and thin white hit connectors (RGB 255,255,255) from emitter to receiver.

## Controls and kinematics
- Architrino speed is user-settable from near zero up to and beyond field speed.
- Above field speed, depict self-hits using the same rules as partner hits.
- Any control change that alters the current field depiction or emitter-to-target lines forces a restart from the initial state.
- Control panel exposes an architrino speed multiplier on path speed in [0, 100]; multiplier 0 means stationary on the path.
- Self-hits are disallowed when the speed multiplier is ≤ 1; permit self-hits only when speed exceeds field speed.

## Hits and diagnostics
- A hit occurs at times $t$ and emissions $t_0$ satisfying $\|\mathbf{s}_r(t) - \mathbf{s}_e(t_0)\| = v\,(t - t_0)$; display the emitter position $\mathbf{s}_e(t_0)$ at that hit time.
- Log hits on the positrino: record strength proportional to $1/r^2$ and polar angle $\theta \in [0, 2\pi)$ measured from the $+x$ axis.
- Hit table formatting: text color follows receiver polarity (pure red for positrino hits, pure blue for electrino hits). Columns: receiver angle at $t=\text{now}$ (relative to origin), hit angle, superimposed hit strength, hit index (for multiple hits).
- In hit tables/indicators, color entries by emitter (pure red or pure blue); self-hits use the receiver’s color.
- Hit table includes the current architrino speed multiplier.
- Support exporting screenshots in PNG/JPG now; plan for MOV animation export later.

# Design
Three-layer architecture:
- Numerical engine computes orbit paths, retarded times, causal shells.
- Field engine computes per-frame field grids (CPU with Numba or GPU shaders).
- Rendering engine displays the field texture and overlays geometry; UI layer handles keyboard/mouse controls for speed multipliers, pause, and mode toggles.

Recommended flow:
- Physics engine (Python + NumPy + Numba) computes trajectories and retarded-time effects.
- Field engine maps field values to RGB textures each frame (Numba or GLSL).
- Rendering engine (PyGame or ModernGL) composites the field texture with geometric primitives and exports frames when requested.

# Technology
Options (updated for predefined paths and optional precomputed frames):

## CPU raster + overlays (PyGame + NumPy + Numba)
- Why: Direct pixel control for superposition coloring; straightforward to precompute frame textures for a given path library and play them back smoothly.
- Sketch: For each time step, compute per-pixel field from predefined trajectories (NumPy/Numba), bake to RGB frame, store to disk/ram; playback via PyGame with UI overlays (markers, hit lines, tables).
- Pros: Simple pipeline; offline precompute avoids runtime spikes; easy control of color mapping and scaling.
- Cons: CPU-bound; very high resolutions or many particles may take time to pre-bake.

## GPU shading (ModernGL + GLSL)
- Why: Real-time per-pixel field shading when interactive parameter changes (e.g., path reversal, speed) must reflect immediately without re-baking.
- Sketch: Vertex layer draws markers/geometry; fragment shader evaluates superposition and shading per pixel; CPU passes path parameters and uniforms.
- Pros: Highest interactive performance; minimal precomputation needed.
- Cons: Shader complexity and debugging overhead; less convenient for hit-table extraction unless mirrored on CPU.

## Offline render + video (NumPy/Numba + imageio/ffmpeg)
- Why: For guaranteed smooth playback, pre-bake all frames to an image stack or video; UI scrubs over frames.
- Sketch: Generate frames offline using the same CPU kernels; encode with ffmpeg; load frames for scrubbing/playback.
- Pros: Maximal smoothness; deterministic output; easy to export media.
- Cons: Large storage for long runs; parameter changes require re-render.

### Recommended approach
- Core: CPU pipeline (NumPy + Numba) with an option to precompute/bake frames per chosen path and speed, then play back via a lightweight UI (PyGame/pyglet) with overlays and hit tables.
- Performance tier: Add ModernGL shader path if we need live, no-bake updates at high resolution.
- Export: Use ffmpeg/imageio for video or frame export.
- Hardware note: Apple Silicon GPUs are Metal-capable but not CUDA; use CPU/Metal-friendly stacks (NumPy/Numba/OpenGL/Metal-backed GL where available).

# Performance and platform targets
- Target 4K render/export resolution; on-device playback should accommodate the default first-gen Apple Silicon MacBook display resolution (e.g., 2560×1600), with downscaling if needed.
- Target 30 fps by default; provide user control to lower fps if performance requires.
- Use latest installable Python and compatible packages (NumPy, Numba, PyGame/pyglet, optional ModernGL, ffmpeg/imageio for export).
- Default render duration: run until emissions have colored all pixels in the current canvas extent for the selected path/speed; allow pre-bake to stop once coverage is achieved.
- Memory budget: assume ~24 GB available; allow using a reasonable fraction for frame caching, with optional streaming/tiling if needed.

# Validation
- Verify neutrality renders as pure purple at zero superposition.
- Sanity-check angular measurements (receiver angle vs. hit angle) on the default unit-circle path.
- Confirm hit logging strength follows $1/r^2$ and matches visual hit connectors.
- Smoke-test frame export (PNG/JPG) and fps selection without desynchronization between field and overlays.
