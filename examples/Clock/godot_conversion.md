# Godot Conversion Design: Manim Clock Example

## 1. Goal

Convert the Manim script `examples/Clock.py` into a fully programmatic Godot 4 project. The Godot version should replicate the original functionality:
- Display an analog clock face with hour, minute, and second hands.
- Update hands based on system time, with modified speeds (hour 0.5x, minute 10x, second 2x).
- The entire clock assembly should move along a predefined parametric path.
- The implementation should prioritize programmatic node creation and scene setup, minimizing reliance on the Godot Editor GUI, as per `README_godot.md`.

## 2. Godot Project Structure

Following the recommendation in `README_godot.md` for separate projects per example:

- **Project Root:** `examples/Clock/`
- **Main Scene Script:** `clock_main.gd` (attached to the root Node3D)
- **Clock Assembly Script:** `clock_assembly.gd` (using `class_name ClockAssembly`, attached to a Node3D representing the clock)
- **Configuration:** `project.godot`

No `.tscn` files will be manually created in the editor. All nodes will be instantiated and configured via GDScript.

## 3. Step-by-Step Conversion Plan

### Step 0: Project Setup

1.  **Create Directory:** Ensure the `examples/Clock/` directory exists.
2.  **Create `project.godot`:** Programmatically create `examples/Clock/project.godot`.
    *   Set `config/name` to "Clock".
    *   Set `application/run/main_scene` to `"clock_main.gd"` (we'll create this script as the entry point).
    *   Set `display/window/size/viewport_width` and `viewport_height` (e.g., 1920x1080).
    *   Set the default clear color to Indigo (`Color(0.294118, 0, 0.509804, 1)`) in the `[rendering]` section as seen in `examples/anglepath/project.godot`.
    *   Include the default `icon.svg` (copy if necessary).
3.  **Create `.gitignore`:** Add standard Godot entries (`.godot/`, etc.) and potentially `.gdignore` if needed later.

### Step 1: `ClockAssembly` Node and Script (`clock_assembly.gd`)

1.  **Create File:** Create `examples/Clock/clock_assembly.gd`.
2.  **Define Class:**
    ```gdscript
    # clock_assembly.gd
    class_name ClockAssembly
    extends Node3D

    # --- Constants ---
    const WHITE: Color = Color.WHITE
    const BLUE: Color = Color.BLUE
    const GREEN: Color = Color.GREEN
    const RED: Color = Color.RED
    const YELLOW_A: Color = Color(1.0, 1.0, 0.0, 0.7) # Example, adjust alpha as needed

    # --- Properties ---
    var radius: float = 2.0 # Default, can be set on instantiation

    # References to MeshInstance3D nodes for dynamic parts
    var hour_hand: MeshInstance3D
    var minute_hand: MeshInstance3D
    var second_hand: MeshInstance3D
    var center_dot: MeshInstance3D

    # References to static parts (optional, if needed later)
    var face_circle: MeshInstance3D
    var minute_ticks_mesh: MeshInstance3D
    var hour_ticks_mesh: MeshInstance3D

    # --- Initialization ---
    func _init(p_radius: float = 2.0):
        radius = p_radius

    func _ready() -> void:
        _create_static_elements()
        _create_dynamic_elements()
        _update_hands() # Set initial position
    ```
3.  **Add Docstrings:** Add initial docstrings explaining the class purpose.

### Step 2: Create Static Clock Elements (in `clock_assembly.gd`)

1.  **Implement `_create_static_elements`:** This function will create the clock face, ticks, and center dot programmatically.
2.  **Drawing Method:** Use `ImmediateMesh` for drawing lines (ticks) and potentially the circle outline. Alternatively, use `MeshInstance3D` with primitive meshes (`TorusMesh` for the face, `CylinderMesh` or `BoxMesh` for ticks). `ImmediateMesh` offers more direct control similar to Manim's `Line`. Let's proceed with `ImmediateMesh`.
3.  **Face Circle:**
    *   Create a `MeshInstance3D` node (`face_circle`).
    *   Create an `ImmediateMesh` resource.
    *   Use `surface_begin(Mesh.PRIMITIVE_LINE_STRIP)`.
    *   Calculate points around a circle (radius `radius`) using `sin`/`cos` for a sufficient number of segments (e.g., 64).
    *   Add vertices using `surface_add_vertex`. Remember to close the loop.
    *   Set material override for the `MeshInstance3D` to control color (WHITE) and potentially thickness (using spatial material properties if needed, though `ImmediateMesh` line thickness isn't directly controllable like Manim's stroke width - consider using thin `CylinderMesh` or `BoxMesh` if thickness is critical). For simplicity, start with `ImmediateMesh`.
    *   `surface_end()`.
    *   Assign the mesh to the `MeshInstance3D`.
    *   Add the `MeshInstance3D` as a child of `ClockAssembly`.
4.  **Minute Ticks:**
    *   Create one `MeshInstance3D` node (`minute_ticks_mesh`).
    *   Create an `ImmediateMesh`.
    *   Use `surface_begin(Mesh.PRIMITIVE_LINES)`.
    *   Loop 60 times (angle = `i * TAU / 60.0`).
    *   Calculate start point (`radius * Vector3(cos(angle), sin(angle), 0)`) and end point (`0.95 * radius * Vector3(cos(angle), sin(angle), 0)`).
    *   Add both vertices (`surface_add_vertex`) for each line segment.
    *   Set material override (WHITE).
    *   `surface_end()`.
    *   Assign mesh and add as child.
5.  **Hour Ticks:**
    *   Similar to minute ticks, but create `hour_ticks_mesh`.
    *   Loop 12 times.
    *   Use end point factor `0.85 * radius`.
    *   Set material override (WHITE). Consider if thicker lines are needed (might require switching to `CylinderMesh`/`BoxMesh` per tick if `ImmediateMesh` lines are too thin). Start with `ImmediateMesh`.
    *   Assign mesh and add as child.
6.  **Center Dot:**
    *   Create `center_dot` as `MeshInstance3D`.
    *   Use a `SphereMesh` resource. Set its `radius` (e.g., 0.05).
    *   Create a `StandardMaterial3D` resource, set `albedo_color` to WHITE.
    *   Assign mesh and material.
    *   Set `z_index` or ensure it's added last/has appropriate material settings to render on top. Godot's 3D rendering order is complex; consider material `render_priority` or transparency settings if layering issues occur. Start simply by adding it after hands.
    *   Add as child.

### Step 3: Create Clock Hands (in `clock_assembly.gd`)

1.  **Implement `_create_dynamic_elements`:** This function initializes the hand nodes.
2.  **Hour Hand:**
    *   Create `hour_hand` as `MeshInstance3D`.
    *   Create an `ImmediateMesh`.
    *   `surface_begin(Mesh.PRIMITIVE_LINES)`.
    *   Define start (ORIGIN - `Vector3.ZERO`) and end (`Vector3(0, radius * 0.5, 0)` - pointing UP initially).
    *   Add vertices.
    *   `surface_end()`.
    *   Create `StandardMaterial3D`, set `albedo_color` to BLUE. Set `shading_mode` to `BaseMaterial3D.SHADING_MODE_UNSHADED` if lighting is not desired.
    *   Assign mesh and material.
    *   Add as child.
3.  **Minute Hand:** Similar to hour hand, create `minute_hand`, use end point `Vector3(0, radius * 0.7, 0)`, color GREEN. Add as child.
4.  **Second Hand:** Similar, create `second_hand`, use end point `Vector3(0, radius * 0.8, 0)`, color RED. Add as child.
5.  **Layering:** Add the `center_dot` *after* the hands in the `_ready` function to ensure it draws on top initially. Fine-tune with material properties (`render_priority`, transparency) if needed during updates.

### Step 4: Implement Hand Update Logic (in `clock_assembly.gd`)

1.  **Create `_process(delta)` function:** This will call `_update_hands`.
2.  **Implement `_update_hands` function:**
    *   Get current time using `Time.get_datetime_dict_from_system()`.
    *   Calculate target angles (similar logic to Manim's `update_hands`):
        *   `hour`, `minute`, `second` from the time dictionary.
        *   Apply speed modifiers: `hour_progress = (hour % 12 + minute / 60.0 + second / 3600.0) * 0.5`
        *   `minute_progress = (minute + second / 60.0) * 10.0`
        *   `second_progress = (second * 2.0)`
        *   Convert progress to angles (remembering Godot's coordinate system: Y-up, rotations are often around Z for 2D-like behavior in XY plane, positive angle is counter-clockwise). Manim's calculation `-(...) + PI/2` converts fraction to clockwise angle starting from UP. Replicate this logic carefully.
        *   `target_hour_angle = -((hour_progress / 12.0) * TAU) + PI / 2.0`
        *   `target_minute_angle = -(((minute_progress % 60.0) / 60.0) * TAU) + PI / 2.0`
        *   `target_second_angle = -(((second_progress % 60.0) / 60.0) * TAU) + PI / 2.0`
    *   **Update Hand Rotations:**
        *   Reset rotation: `hour_hand.rotation = Vector3(0, 0, 0)` (or store initial UP orientation).
        *   Apply new rotation: `hour_hand.rotation.z = target_hour_angle` (assuming Z is the axis perpendicular to the clock face). Adjust axis if needed based on node orientation. Use `rotate_z(target_hour_angle)` if preferred.
        *   Repeat for `minute_hand` and `second_hand`.
        *   *Alternative:* Instead of resetting and setting absolute rotation, calculate the difference from the *current* rotation and use `rotate_z()`. However, the absolute method used in the Manim `become` logic is likely more robust. Let's stick to setting the absolute `rotation.z`.

### Step 5: Main Scene Setup (`clock_main.gd`)

1.  **Create File:** Create `examples/Clock/clock_main.gd`.
2.  **Define Class:**
    ```gdscript
    # clock_main.gd
    extends Node3D

    # Preload the ClockAssembly script/scene if it were a .tscn
    # Since it's just a script, we'll instantiate it directly.
    # const ClockAssembly = preload("res://clock_assembly.gd") # Not needed if instantiating script

    var clock_assembly_instance: ClockAssembly
    var path_node: Path3D
    var path_follow_node: PathFollow3D
    var path_visualization_mesh: MeshInstance3D # Optional

    func _ready() -> void:
        _setup_environment()
        _create_path()
        _create_clock()
        _setup_path_following()
        _start_animation()

    func _setup_environment() -> void:
        # Background color is set in project.godot
        # Add lighting if needed (e.g., DirectionalLight3D)
        var light = DirectionalLight3D.new()
        light.light_energy = 1.0
        light.shadow_enabled = true
        add_child(light)

        # Add Camera
        var camera = Camera3D.new()
        camera.position = Vector3(0, 0, 10) # Adjust position to see the clock
        camera.look_at(Vector3.ZERO)
        add_child(camera)
    ```

### Step 6: Create Parametric Path (in `clock_main.gd`)

1.  **Implement `_create_path`:**
    *   Create `path_node = Path3D.new()`. Add as child.
    *   Create `var curve = Curve3D.new()`.
    *   Define the parametric function: `func path_func(t: float) -> Vector3: return Vector3(3.0 * sin(t * 2.0), 2.0 * cos(t * 3.0), 0)`
    *   Sample points along the curve: Loop `t` from 0 to `TAU` with a suitable step (e.g., 100 steps).
    *   For each `t`, calculate the point using `path_func(t)`.
    *   Add points to the curve: `curve.add_point(path_func(t))`.
    *   Assign the curve to the path node: `path_node.curve = curve`.
    *   **(Optional) Visualize Path:** Create `path_visualization_mesh` using `ImmediateMesh` (similar to clock face circle, but using the calculated path points) with `YELLOW_A` color. Add as child.

### Step 7: Instantiate Clock (in `clock_main.gd`)

1.  **Implement `_create_clock`:**
    *   Instantiate the assembly: `clock_assembly_instance = ClockAssembly.new(2.0 * 0.95 * 0.95)` (passing the adjusted radius).
    *   Set a name: `clock_assembly_instance.name = "ClockAssemblyInstance"`
    *   *Crucially, do NOT add it as a direct child yet.* It will be added under `PathFollow3D`.

### Step 8: Setup Path Following (in `clock_main.gd`)

1.  **Implement `_setup_path_following`:**
    *   Create `path_follow_node = PathFollow3D.new()`.
    *   Set `path_follow_node.rotation_mode = PathFollow3D.ROTATION_ORIENTED` (or other modes if needed).
    *   Set `path_follow_node.loop = true` (Manim's `MoveAlongPath` doesn't explicitly loop, but the animation duration might imply it; let's make it loop for continuous movement).
    *   Add `clock_assembly_instance` as a child of `path_follow_node`.
    *   Add `path_follow_node` as a child of `path_node`.

### Step 9: Animate Along Path (in `clock_main.gd`)

1.  **Implement `_start_animation`:**
    *   Use a `Tween` for smooth, continuous movement.
    *   `var tween = create_tween().set_loops().set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)`
    *   Animate the `progress_ratio` property of `path_follow_node` from 0.0 to 1.0 over the desired duration (Manim uses 15 seconds).
    *   `tween.tween_property(path_follow_node, "progress_ratio", 1.0, 15.0).from(0.0)`
    *   *Note:* `progress_ratio` goes from 0 to 1. Manim's `run_time` controls the duration. The `set_loops()` makes it continuous.

### Step 10: Refinement and Cleanup

1.  **Review Code:** Ensure all GDScript code adheres to the standards in `README_prompts.md` (type hints, docstrings, formatting).
2.  **Constants:** Define colors and magic numbers (like hand length factors) as constants where appropriate.
3.  **Coordinate Systems:** Double-check angle calculations and rotations match Godot's 3D coordinate system (Y-up, Z-out, counter-clockwise rotation).
4.  **Performance:** For many ticks/hands, `ImmediateMesh` might be less performant than using instancing (`MultiMeshInstance3D`) or individual `MeshInstance3D` with primitive meshes. Start with `ImmediateMesh` for simplicity, optimize if needed.
5.  **Manim `wait(2)`:** The Godot version runs continuously via the tween loop. The final `wait` isn't directly applicable unless the tween is stopped.
6.  **Updater Removal:** Manim removes the updater. In Godot, the `_process` function in `ClockAssembly` runs continuously. If the clock needed to stop updating, a flag (`var active = true`) could be added and checked in `_process`. For this conversion, continuous updates are fine.

## 4. Verification

1.  Run the Godot project using the command line: `godot --path examples/Clock`
2.  Verify:
    *   Clock face, ticks, and hands are drawn correctly with specified colors.
    *   Hands update according to system time with the correct speed modifications.
    *   The entire clock assembly moves smoothly along the yellow parametric path.
    *   The background color is Indigo.
    *   Check for console errors.

This detailed plan provides a step-by-step guide for converting the Manim `Clock.py` example into a programmatic Godot project, suitable for implementation by an AI agent.

## Workflow Automation

### Options to Make Video

- record window while running in Godot app.
- save frames and stitch them together

### Run Godot and Write Frames

- /Applications/Godot.app/Contents/MacOS/Godot angle_path.tscn --write-movie movie_frames/frame_%04d.png --movie-fps 60 --quit-after 900
- Issue: The '%04d' portion needs fixing. Had to patch filenames up.

### Stitch Frames into Video

- ffmpeg -framerate 60 -i movie_frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 output_video.mp4
- Issue: produced a .mov file? Why?
