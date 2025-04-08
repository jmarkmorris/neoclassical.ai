# Godot Conversion Plan: CircleSizes

This plan outlines the steps to recreate the Manim `CircleSizes` visualization in Godot Engine. The goal is to match the appearance shown in `examples/CircleSizes/goal.jpg`.

**Target Visuals:**
*   Indigo background.
*   Electric purple grid lines.
*   A grid of cells, each containing two circles (blue left, red right) and a text label below them.
*   Circle radius increases incrementally for each cell, moving left-to-right, top-to-bottom.
*   Labels display the current radius formatted to three decimal places.

**Core Concepts:**
*   Use Godot's 3D nodes (`Node3D`, `MeshInstance3D`, `Label3D`).
*   Replicate the nested loop structure for grid generation.
*   Map Manim's coordinate system and radius values to Godot's 3D world coordinates and units.
*   Use `Label3D` nodes for text display.
*   Use `MeshInstance3D` with `SphereMesh` for circles and thin `CylinderMesh` or `BoxMesh` for grid lines.

---

## Step 1: Project Setup

1.  **Create Godot Project:** Start a new Godot project.
2.  **Main Scene:** Create a main 3D scene (e.g., `CircleSizes.tscn`) with a `Node3D` as the root. Add a `Camera3D` and position it appropriately (e.g., looking along the Z-axis at the XY plane). Add a `WorldEnvironment` node with an environment resource to control background color and lighting.
3.  **Script:** Attach a new GDScript (e.g., `CircleSizes.gd`) to the root `Node3D`.
4.  **Define Colors:** In the script, define the required colors as constants or variables:
    ```gdscript
    const INDIGO = Color("#4B0082")
    const ELECTRIC_PURPLE = Color("#8F00FF")
    const PURE_BLUE = Color.BLUE # Or Manim's specific blue if needed
    const PURE_RED = Color.RED   # Or Manim's specific red if needed
    const WHITE = Color.WHITE
    ```

## Step 2: Background and Coordinate System Planning

1.  **Set Background:** In the `WorldEnvironment` node's environment resource, set the Background Mode to `Color` and the Background Color to `INDIGO`. Add a `DirectionalLight3D` for basic illumination if needed for materials.
2.  **Coordinate Mapping:**
    *   Manim uses a grid from `x=[-7, 7]` and `y=[-4, 4]`. We can map this directly to Godot's 3D world units on the XY plane (Z=0).
    *   1 Manim unit will correspond to 1 Godot world unit.
    *   The Manim origin (0,0) will correspond to the Godot origin (0,0,0).
    *   Define constants for the Manim grid range.
    *   Create a helper function `map_manim_to_godot(manim_x, manim_y)` that returns a `Vector3(manim_x, manim_y, 0)`.

## Step 3: Create the Grid

1.  **Grid Node:** Create a child `Node3D` named `GridContainer` in `CircleSizes.tscn` to hold the grid lines.
2.  **Grid Script Logic:** In `CircleSizes.gd`'s `_ready()` function:
    *   Define grid line thickness (e.g., `GRID_LINE_THICKNESS = 0.02`).
    *   Define a standard material for the grid lines (`StandardMaterial3D` or `ORMMaterial3D`) with `albedo_color` set to `ELECTRIC_PURPLE` and `shading_mode` set to `unshaded`.
    *   Loop through the Manim X and Y ranges.
    *   For each vertical line:
        *   Create a `MeshInstance3D`.
        *   Set its mesh to a `CylinderMesh` (or `BoxMesh`). Configure height (Manim height), radius/size (half the thickness), and material.
        *   Position the `MeshInstance3D` at the correct X coordinate, centered vertically (Y=0).
        *   Add it as a child of `GridContainer`.
    *   For each horizontal line:
        *   Create a `MeshInstance3D`.
        *   Set its mesh to a `CylinderMesh` (or `BoxMesh`). Configure height (Manim width), radius/size (half the thickness), and material.
        *   *Rotate* the mesh instance by 90 degrees around the Z-axis.
        *   Position it at the correct Y coordinate, centered horizontally (X=0).
        *   Add it as a child of `GridContainer`.

## Step 4: Create a Reusable "Cell" Scene

*   *Rationale:* Encapsulating the circles and label for each grid cell makes instantiation and management easier.

1.  **New Scene:** Create a new scene (`CircleCell.tscn`) with a `Node3D` root.
2.  **Script:** Attach a script (`CircleCell.gd`) to its root.
3.  **Nodes:**
    *   Add two `MeshInstance3D` nodes, named `LeftCircle` and `RightCircle`.
    *   Add a `Label3D` node named `RadiusLabel`.
4.  **Materials:** Create two standard materials (`StandardMaterial3D` or `ORMMaterial3D`), one blue (`mat_blue`) and one red (`mat_red`). Set their `albedo_color` appropriately and set `shading_mode` to `unshaded`.
5.  **Cell Script (`CircleCell.gd`):**
    *   Get node references (`@onready var left_circle = $LeftCircle`, etc.).
    *   Define variables for the blue and red materials (or load them).
    *   Add a function `update_display(manim_radius: float)`:
        *   Store `manim_radius`.
        *   **Circles:**
            *   Set the `mesh` property of `LeftCircle` and `RightCircle` to a `SphereMesh`.
            *   Set the `radius` and `height` of the `SphereMesh` based on `manim_radius`. (Godot radius = Manim radius).
            *   Assign the blue material to `LeftCircle` and red to `RightCircle`.
            *   Position `LeftCircle` relative to the cell origin (e.g., `Vector3(-0.25, -0.25, 0)`) and `RightCircle` (e.g., `Vector3(0.25, -0.25, 0)`). *Note: Adjust these offsets based on Manim script's `move_to` logic relative to the cell center.*
        *   **Label:**
            *   Update the `RadiusLabel.text` property (e.g., `RadiusLabel.text = "r = %.3f" % manim_radius`).
            *   Configure `Label3D` properties: `font_size`, `text_color` (WHITE), `billboard` mode (optional, e.g., `BillboardMode.ENABLED`), horizontal/vertical alignment. Load a font resource.
            *   Position `RadiusLabel` below the circles (e.g., `Vector3(0, -0.75, 0)`). *Adjust based on Manim script.*

## Step 5: Instantiate and Position Cells in Main Scene

1.  **Cell Container:** Create a child `Node3D` named `CellContainer` in `CircleSizes.tscn` to hold all the cell instances.
2.  **Load Cell Scene:** In `CircleSizes.gd`, preload the `CircleCell.tscn`:
    ```gdscript
    const CircleCell = preload("res://CircleCell.tscn") # Adjust path if needed
    ```
3.  **Implement Loops:** In the `_ready()` function of `CircleSizes.gd` (after grid creation):
    *   Get reference to `CellContainer` (`@onready var cell_container = $CellContainer`).
    *   Replicate the nested `for` loops from the Manim script.
    ```gdscript
    var current_radius = 0.002
    const RADIUS_INCREMENT = 0.002

    # Manim loops from y=4 down to y=-3, and x=-7 to x=6
    for y_manim in range(4, -4, -1):
        for x_manim in range(-7, 7):
            # Instantiate cell
            var cell_instance = CircleCell.instantiate()

            # Configure cell
            cell_instance.update_display(current_radius)

            # Calculate position for the *center* of the Manim cell
            # Manim positions circles/labels relative to the integer grid point (x, y)
            # which acts as the bottom-left corner of the conceptual cell in the loop.
            # The visual cell center seems to be (x+0.5, y-0.5) in Manim coords.
            var cell_center_manim = Vector3(float(x_manim) + 0.5, float(y_manim) - 0.5, 0.0)
            cell_instance.position = cell_center_manim # Direct mapping

            # Add to scene tree under the container
            cell_container.add_child(cell_instance)

            # Increment radius
            current_radius += RADIUS_INCREMENT
    ```
4.  **Adjust Loop Ranges:** The Manim loops `range(4, -4, -1)` (y) and `range(-7, 7)` (x) define the grid points used as centers/anchors. Ensure the Godot loops match these ranges exactly to place cells correctly.

## Step 6: Refinement and Styling

1.  **Camera Position:** Adjust the `Camera3D`'s position (especially Z distance) and projection (Perspective or Orthogonal) to frame the grid nicely. Orthogonal projection might match the Manim view better. Adjust the camera's `size` property if using Orthogonal projection.
2.  **Circle/Label Positioning:** Fine-tune the relative positions of the `LeftCircle`, `RightCircle`, and `RadiusLabel` within `CircleCell.tscn` to precisely match the layout in `goal.jpg`. Use the Manim script's offsets (`[x + 0.25, y-0.25, 0]`, `[x + 0.75, y-0.25, 0]`, `[x + 0.5, y-0.75, 0]`) as a guide. Remember these are relative to the cell's origin, which we placed at the Manim cell center `(x+0.5, y-0.5)`.
    *   Left Circle Manim: `(x+0.25, y-0.25)` -> Relative: `(-0.25, 0.25)`
    *   Right Circle Manim: `(x+0.75, y-0.25)` -> Relative: `(0.25, 0.25)`
    *   Label Manim: `(x+0.5, y-0.75)` -> Relative: `(0, -0.25)`
    *   *Correction:* Manim's `move_to` uses the center of the object. The grid points `(x,y)` seem to be the *center* of the cells visually in the Manim output. Let's adjust Step 5 positioning and these relative positions. Revert cell center calculation in Step 5. Position cell instance at `Vector3(float(x_manim), float(y_manim), 0.0)`. Then relative positions in `CircleCell` become:
        *   Left Circle: `Vector3(0.25, -0.25, 0)`
        *   Right Circle: `Vector3(0.75, -0.25, 0)`
        *   Label: `Vector3(0.5, -0.75, 0)`
3.  **Font:** Load a suitable font (like Inter or Roboto) as a Godot resource (`.tres` FontFile). Apply it to the `Font` property of the `Label3D` node in `CircleCell.tscn`. Adjust `Label3D`'s `font_size` (this is in world units, so might be small, e.g., 0.1 or 0.2).
4.  **Grid Lines:** Adjust `GRID_LINE_THICKNESS` and ensure the grid lines align correctly with the cell centers. Check the positioning logic in Step 3.
5.  **Materials:** Ensure circle materials are `unshaded` to match the flat look.
6.  **Testing:** Run the scene frequently to check progress and make adjustments.

---
