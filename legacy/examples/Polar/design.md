# Godot Polar Coordinates Visualization Design

## 1. Goal

The objective is to create a 3D scene in Godot Engine that visually replicates the elements shown in the reference image `examples/PolarCoordinates/goal.jpg`. This includes a title, a polar coordinate grid, and a vector originating from the center. The subtitle text from the image should be omitted.

## 2. Scene Setup

*   **Root Node:** The main scene root will be a `Node3D`.
*   **Camera:** A `Camera3D` should be added to the scene, positioned to provide a clear view of the visualization elements, likely looking along the negative Z-axis towards the origin. Consider using an orthogonal projection for a flat 2D look consistent with the reference image.
*   **Background:** The default clear color should be set to Indigo (`#4B0082`), matching the reference image background. This can be configured in Project Settings -> Rendering -> Environment -> Default Clear Color.

## 3. Title

*   **Node:** Use a `Label3D` node for the title.
*   **Text:** Set the text to "Polar Coordinates Visualization".
*   **Appearance:**
    *   Font: Choose a clean, sans-serif font (similar to Helvetica Neue Light if available, otherwise a default sans-serif).
    *   Font Size: Adjust the `Label3D` font size and pixel size properties to achieve a size comparable to the reference image (relative to the viewport).
    *   Color: Set the text color to white.
    *   Outline: No outline.
*   **Positioning:** Position the `Label3D` node near the top edge of the viewport, centered horizontally.

## 4. Polar Grid

A `Node3D` should serve as the parent container for all grid elements to allow easy positioning. Position this container slightly below the viewport center (e.g., `(0, -0.5, 0)` in global coordinates, adjust as needed). All grid elements should lie on the XY plane (Z=0 relative to the container).

*   **Grid Lines Material:** Create a `StandardMaterial3D` for all grid lines (circles and radial lines).
    *   Albedo: White (`#FFFFFF`).
    *   Shading: Set `Shading Mode` to `Unshaded`.
    *   Line Width: Use `MeshInstance3D` with appropriate mesh generation (e.g., `ImmediateMesh`) or multiple thin `MeshInstance3D` nodes (like scaled `CylinderMesh` or `BoxMesh` for lines if `ImmediateMesh` line width is problematic). Aim for a line thickness visually similar to the reference (approx 1.8 pixels in the Manim reference, translate appropriately).

*   **Concentric Circles:**
    *   Generate meshes representing circles centered at the grid container's origin.
    *   Radii: 1.0, 2.0, 3.0, 4.0.
    *   Mesh Type: Use `ImmediateMesh` with `PrimitiveType = Mesh.PRIMITIVE_LINE_STRIP` or generate thin torus meshes (`TorusMesh`).
    *   Assign the white unshaded material.

*   **Radial Lines:**
    *   Generate meshes representing lines starting from the grid origin and extending to the outermost circle (radius 4.0).
    *   Angles: Draw lines at angles corresponding to 0, π/6, π/3, π/2, 2π/3, 5π/6, π, 7π/6, 4π/3, 3π/2, 5π/3, 11π/6 radians (12 lines total, every 30 degrees).
    *   Mesh Type: Use `ImmediateMesh` with `PrimitiveType = Mesh.PRIMITIVE_LINES` or generate thin line meshes.
    *   Assign the white unshaded material.

*   **Labels Material:** Create a base material for labels (can be reused or duplicated).
    *   Albedo: White (`#FFFFFF`).
    *   Shading: Set `Shading Mode` to `Unshaded`.

*   **Radius Labels:**
    *   Nodes: Use `Label3D` nodes for each label.
    *   Text: "1.0", "2.0", "3.0", "4.0".
    *   Positioning: Place each label along the positive X-axis (0 angle line), just outside the corresponding circle radius. Adjust vertical alignment as needed.
    *   Appearance: Use the white unshaded material. Adjust font size for clarity (similar to reference).

*   **Azimuth Labels:**
    *   Nodes: Use `Label3D` nodes for each label.
    *   Text: "0", "π/6", "π/3", "π/2", "2π/3", "5π/6", "π", "7π/6", "4π/3", "3π/2", "5π/3", "11π/6". Use appropriate characters for π.
    *   Positioning: Place each label just outside the largest circle (radius 4.0), aligned with its corresponding radial line. Ensure the text is oriented upright relative to the camera view.
    *   Appearance: Use the white unshaded material. Adjust font size for clarity (similar to reference).

## 5. Vector

*   **Node:** Use a `MeshInstance3D` to represent the vector arrow.
*   **Mesh:** Create a mesh representing an arrow. This can be:
    *   A thin cylinder or box for the line segment.
    *   A cone (`ConeMesh`) or pyramid shape for the arrowhead.
    *   These can be combined using `ArrayMesh` or by parenting the arrowhead mesh to the line mesh node.
*   **Positioning & Orientation:**
    *   Origin: The base of the vector line should be at the grid container's origin.
    *   Endpoint: The tip of the vector (base of the arrowhead) should correspond to the polar coordinates (r=2.4, θ=π/4). Calculate the Cartesian coordinates: `x = 2.4 * cos(π/4)`, `y = 2.4 * sin(π/4)`, `z = 0`.
    *   Orientation: The mesh should be rotated and scaled appropriately to span from the origin to the calculated endpoint.
*   **Material:** Create a `StandardMaterial3D`.
    *   Albedo: Red-Orange (e.g., `#FF4500` or similar, matching the reference `RED_E`).
    *   Shading: Set `Shading Mode` to `Unshaded`.

## 6. References

*   **Target Visual:** `examples/PolarCoordinates/goal.jpg`
*   **Parameter Reference:** `examples/PolarCoordinates/PolarCoordinates.py` (for specific values like background color, vector coordinates r=2.4, θ=π/4, line counts/angles, radii).

## 7. Exclusions

*   The subtitle text ("PolarPlane(...) + Vector(...)") present in the reference image and Python script should not be included in the Godot scene.
*   No animation is required for this initial implementation.
