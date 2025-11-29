# Project
Build a continuously animated 2-D dynamical geometry visualizer for orbiting partner charges, showing per-pixel field computations plus geometric overlays (orbits, retarded-position lines, causal shells) with interactive playback and exportable frames.

# Requirements
1. Maintain smooth interactive animation (target 30–60 fps).
2. Compute per-pixel scalar/vector fields that evolve over time.
3. Draw geometric primitives: circles, orbits, rays, retarded-position lines, causal shells.
4. Provide playback controls: pause, scrub, change particle speed, “beyond field speed” mode.
5. Export frames or movies for downstream visualization.

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
Options:

## PyGame + NumPy + Numba
- Why: Full pixel control with near-C speed CPU kernels; deterministic timing; easy geometric overlays.
- Sketch: PyGame main loop, 2-D NumPy potential grid, Numba kernels for field contributions using retarded times, grid → RGB map → PyGame surface, overlays via PyGame primitives, optional PNG frame exports.
- Pros: Maximum flexibility; fast enough for ~1000×1000 grids when optimized; easy to extend geometry.
- Cons: You write most pieces; no native vector graphics.

## ModernGL (OpenGL) + GLSL shaders
- Why: GPU fragment shaders evaluate F(x,y,t) per pixel for high-res real-time fields; Python (moderngl) supplies geometry and uniforms.
- Sketch: moderngl window, fragment shader computes colors from charge worldlines and retarded-time equations, vertex layer draws circles/rays/orbits; GPU yields ~100× field speed.
- Pros: Fastest path; smooth 4K animation; ideal for “fields that look alive.”
- Cons: Requires GLSL; shader debugging is more tedious.

## Manim (geometry-first, slower fields)
- Why: Strong for circles, rays, angles, orbit paths, causal lines; math-scene abstraction; polished video export.
- Gap: Per-pixel dynamic fields with history will bottleneck; not GPU-accelerated. Works best for the geometry layer, not as a live field renderer.

### Recommended stack
- Primary: PyGame (or pyglet) + NumPy + Numba for physics/field/render loop and UI controls.
- Optional: ModernGL fragment shader for GPU-fast field shading when resolution demands it.
- Note on hardware: Apple Silicon Macs have an integrated on-die GPU (Metal-capable, not CUDA); Metal-backed libraries run well, CUDA-only stacks will not.
