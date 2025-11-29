# High-Level Design

## Overview
Render a 2-D timespace slice with predefined architrino trajectories, delayed circular emissions, and per-pixel superposition coloring. Support two execution modes: live (compute fields on the fly) and pre-baked (compute frames once, then play back smoothly).

## Core components
- **Trajectory Library**: Parameterized, piecewise-smooth paths in $(x,y,t)$ with direction-reversal option; supplies architrino positions and velocities per time step.
- **Field Engine**: Computes per-pixel scalar potential from delayed shells (radius $r = v\,\tau$, magnitude $1/r^2$) for each emission event; supports linear/log scaling for visualization.
- **Renderer**: Maps field values to RGB (red/blue superposition, purple at neutrality) and draws overlays (architrino markers, emitter markers, causal shells, retarded lines, hit connectors).
- **Hit Detector**: Finds causal roots satisfying $\|\mathbf{s}_r(t) - \mathbf{s}_e(t_0)\| = v\,(t - t_0)$; records hit strength ($\propto 1/r^2$) and angle $\theta \in [0,2\pi)$; colors hit entries by emitter polarity.
- **UI Layer**: Layout with dominant visualization pane and control strip for start/restart/pause, scrub, speed multipliers, overlay toggles, scaling mode, and path selection.
- **Playback/Export**: Plays live-computed frames or pre-baked frames; exports image stacks or video via ffmpeg/imageio.

## Data flow (pre-baked mode)
1) Select path, speed profile, duration, and resolution.  
2) Trajectory Library emits $(\mathbf{s}(t), \mathbf{v}(t))$ samples.  
3) Field Engine computes per-frame field textures; Hit Detector logs hits.  
4) Frames (RGB) + hit tables serialized to disk (or RAM cache).  
5) Renderer/UI loads frames for smooth playback and scrubbing; overlays hit info and markers.  

## Data flow (live mode)
1) UI sets current path and parameters.  
2) Per-frame: Trajectory Library -> Field Engine (NumPy/Numba or GLSL) -> Hit Detector.  
3) Renderer composites field + overlays; UI events adjust speed/scrub/toggles in real time.  

## Performance tiers
- **CPU Tier**: NumPy + Numba for field and hit computation; PyGame/pyglet for rendering and UI; optional pre-bake for smooth playback.
- **GPU Tier**: ModernGL + GLSL for per-pixel shading when immediate, no-bake updates are required; CPU mirrors hit detection for logging/table outputs.

## Extensibility
- Add new paths, speed profiles, or additional architrinos by extending the Trajectory Library.
- Introduce alternative color maps or scaling functions in the Field Engine.
- Swap playback backend (e.g., browser canvas/WebGL) while reusing the same pre-baked assets and logs.
