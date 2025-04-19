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

# Implementation Plan

1.  **Project Setup:**
    *   Create a new Godot 4.x project.
    *   Use the existing `node_3d.tscn` as the main scene.
    *   Create and attach a new GDScript named `main.gd` to the root `Node3D` in `node_3d.tscn`.

2.  **Basic Scene Setup (`main.gd` - `_ready` function):**
    *   **Camera:** Create a `Camera3D` node, position it to view the origin (e.g., at `Vector3(0, 0, 15)` looking towards `-Z`), and make it the current camera.
    *   **Environment:** Create a `WorldEnvironment` node. Create a new `Environment` resource for it. Set the `Background` mode to `Color` and set the `Background Color` to Indigo (`Color("#4B0082")`).
    *   **Lighting:** Create a `DirectionalLight3D` node for basic illumination.
    *   **Title:**
        *   Create a `Label` node.
        *   Set its `text` property to "Path Tracing Animation".
        *   Configure font properties (requires importing a font like Helvetica Neue Light or using a default, set size to ~36).
        *   Position the label at the top-center of the viewport using `anchor` and `margin` properties or by calculating position based on viewport size. Ensure it uses a `StandardMaterial3D` with `shading_mode = unshaded` and `use_point_size = true` if rendering in 3D space, or consider using a `CanvasLayer` for 2D overlay.

3.  **Particle Definition (`main.gd`):**
    *   Define constants for colors: `INDIGO`, `PURE_BLUE`, `PURE_RED`, `LIGHT_BLUE`, `LIGHT_RED`.
    *   Define particle configurations (e.g., an array of dictionaries, each specifying object color and trail color).
    *   Define particle radius (adjust based on Manim's `0.075` relative to scene scale).

4.  **Path Generation (`main.gd`):**
    *   Create a function `generate_random_path(start_pos, num_points, bounds)`:
        *   Takes a starting position, number of points, and boundary limits.
        *   Initializes a `Curve3D` resource.
        *   Adds the `start_pos`.
        *   Loops `num_points` times:
            *   Generates a random direction (angle in XY plane).
            *   Calculates the next point based on the previous point and a small step in the random direction.
            *   **Clamping:** Checks if the `new_point` is within the specified `bounds` (e.g., X between -7 and 7, Y between -3.75 and 2.5, Z=0). If outside, generate a new random direction until the point is inside.
            *   Adds the valid `new_point` to the `Curve3D` using `add_point()`.
        *   Returns the generated `Curve3D`.
    *   Define screen boundary constants based on camera view and desired constraints.

5.  **Particle and Path Instantiation (`main.gd` - `_ready` function):**
    *   Loop through the particle configurations:
        *   **Particle Mesh:** Create a `MeshInstance3D` node. Assign a `SphereMesh` resource to it, setting its `radius`. Create a `StandardMaterial3D`, set its `albedo_color` to the particle color, and assign it to the mesh.
        *   **Path:** Call `generate_random_path` to create a unique `Curve3D` for this particle, starting near the center (e.g., `Vector3(0, -1, 0)`).
        *   **Path Node:** Create a `Path3D` node and assign the generated `Curve3D` to its `curve` property. Add this `Path3D` to the scene.
        *   **Path Follow:** Create a `PathFollow3D` node. Set its `target` to the `Path3D` node created above. Add the particle's `MeshInstance3D` as a child of this `PathFollow3D`. Add the `PathFollow3D` to the scene.
        *   Store references to the `PathFollow3D` nodes (e.g., in an array).

6.  **Trail Rendering (`main.gd`):**
    *   Choose a method (e.g., `ImmediateMesh`):
        *   For each particle, create an `ImmediateMesh` node. Add it to the scene.
        *   Create a `StandardMaterial3D` for the trail (set `albedo_color` to the trail color, potentially adjust transparency `alpha`, set `shading_mode = unshaded`).
        *   Store references to these `ImmediateMesh` nodes and their corresponding particle `MeshInstance3D` nodes.
        *   Maintain an array (e.g., `trail_points`) for each trail to store `Vector3` positions.
    *   In the `_process(delta)` function:
        *   Loop through each particle's `MeshInstance3D`:
            *   Get its current `global_transform.origin`.
            *   Append this position to the corresponding `trail_points` array.
            *   Access the corresponding `ImmediateMesh` node:
                *   Call `clear_surfaces()`.
                *   Call `surface_begin(Mesh.PRIMITIVE_LINE_STRIP, trail_material)`.
                *   Iterate through the `trail_points` array, calling `surface_add_vertex(point)` for each.
                *   Call `surface_end()`.

7.  **Animation (`main.gd` - `_ready` function):**
    *   Create an `AnimationPlayer` node and add it to the scene.
    *   Create a new `Animation` resource.
    *   Set its `length` to 30 seconds.
    *   For each `PathFollow3D` node stored earlier:
        *   Add a track for its `progress_ratio` property.
        *   Insert a keyframe at time 0 with value 0.
        *   Insert a keyframe at time 30 with value 1.
    *   Assign this `Animation` resource to the `AnimationPlayer`.
    *   Call `play()` on the `AnimationPlayer` with the animation name.

8.  **Final Polish (Optional - `main.gd`):**
    *   Connect to the `AnimationPlayer`'s `animation_finished` signal.
    *   In the connected function, implement a brief visual effect (e.g., using a `Tween` to quickly change the `emission` color or `scale` of the particle meshes).

9.  **Refinement & Export:**
    *   Adjust particle size, trail width/opacity, path complexity (`num_points`), and animation timing for desired visual outcome.
    *   Use Godot's Movie Maker mode or screen recording tools to export the animation as an MP4 video.

