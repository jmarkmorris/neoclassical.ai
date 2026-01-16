# Project Goal
Create a Godot engine mp4 video animation that visually replicates the behavior shown in the reference Manim implementation (`PathTrace.py`) and the provided goal images (`goal1.png` through `goal4.png`).

**Key Visual & Behavioral Requirements:**

1.  **Objects:**
    *   Six point-like objects (represented as small spheres or circles).
    *   Three objects should be pure blue (`#0000FF`).
    *   Three objects should be pure red (`#FF0000`).
2.  **Movement:**
    *   Objects start near the center of the view.
    *   Each object follows a unique, smooth, random path.
    *   Movement should be constrained within the screen boundaries, avoiding overlap with the title/subtitle area at the top.
    *   The overall animation should depict chaotic, overlapping paths similar to `goal4.png`.
3.  **Trails:**
    *   Each object leaves a continuous trail tracing its path.
    *   The trail color should be a lighter shade/hue of the corresponding object's color (e.g., light blue `#ADD8E6` for blue objects, light red/pink `#FFC0CB` for red objects).
    *   Trails should have a thin stroke width and slight transparency (e.g., 50% opacity).
4.  **Scene & Text:**
    *   The background color should be Indigo (`#4B0082`).
    *   Include a main title: "Path Tracing Animation" (Helvetica Neue Light, size 36).
    *   Do not include a subtitle below the title.
5.  **Animation:**
    *   The core movement animation should last approximately 30 seconds.
    *   Consider adding a brief final visual flourish (like the `Flash` in Manim) after the main movement stops.

**Implementation Constraints:**

-   Use Godot Engine (version 4.x assumed).
-   Minimize scene setup in `node_3d.tscn`. Create and configure nodes primarily through GDScript.
-   Reference `PathTrace.py` for logic (random path generation, trail updating) but adapt it idiomatically to Godot's node-based structure and GDScript. Avoid direct translation of Manim-specific classes or functions like `VMobject`, `MoveAlongPath`, or `add_updater`. Use suitable Godot alternatives (e.g., `Curve3D`, `PathFollow3D`, `_process` function, `LineRenderer` or similar for trails).

---

# Updated Implementation Plan

## Boundary Constraint Implementation

1. **Soft Boundary Physics Modification**
   - Implement a force-based boundary constraint mechanism in the `_process` function.
   - Create a new method `_apply_boundary_constraints(particle_pos: Vector3) -> Vector3`:
     * Check if the particle's position is outside the defined boundaries.
     * If outside, apply a soft "pushing" force back towards the center.
     * The force should:
       - Increase exponentially as the particle moves further from the boundary.
       - Be proportional to the distance outside the boundary.
       - Smoothly guide particles back into the animation area without abrupt stops.

2. **Boundary Force Calculation**
   - Develop a quadratic or exponential force function that:
     * Returns zero when inside the boundary.
     * Increases non-linearly as the particle approaches/crosses boundary.
     * Provides a gentle "elastic" constraint.

3. **Boundary Constraint Integration**
   - Modify the force calculation in `_process()`:
     * Before updating particle velocities, apply boundary constraint forces.
     * Ensure these forces are added to the existing Coulomb-like interaction forces.

4. **Tuning Parameters**
   - Add new constants to control boundary behavior:
     * `BOUNDARY_SOFTNESS`: Controls the "elasticity" of boundary constraints.
     * `BOUNDARY_FORCE_MULTIPLIER`: Scales the magnitude of boundary push-back forces.

5. **Visualization Refinement**
   - Ensure trail rendering continues to work smoothly with the new boundary constraints.
   - Verify that particle paths remain visually interesting while staying within bounds.

## Additional Refinement Tasks

1. **Performance Optimization**
   - Profile the current implementation.
   - Optimize force calculations and history tracking if needed.

2. **Randomness Improvement**
   - Review and potentially adjust the random path generation to create more diverse trajectories.

3. **Final Polish
   - Fine-tune animation parameters.
   - Ensure visual consistency with the Manim reference implementation.

## Testing Approach

1. Implement unit tests for:
   - Boundary constraint force calculation
   - Particle position clamping
   - Force magnitude and direction

2. Visual verification:
   - Compare output with goal images
   - Ensure particles stay within defined boundaries
   - Maintain natural, chaotic movement

## Export Considerations

- Use Godot's movie maker or screen recording for MP4 export
- Target 30-second animation duration
- Maintain high-quality rendering settings

