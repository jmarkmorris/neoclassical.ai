# Godot Project Design: Arrow Tips Showcase

## 1. Goal

Create a 2D Godot scene that visually replicates the `examples/ArrowTips/ArrowTips.png` image. The scene will display several examples of axes with different arrow tip styles, along with titles and labels.

## 2. Scene Setup

*   **Root Node:** Use a `Node3D` as the main scene root.
*   **Camera:** Add a `Camera3D` node. Position it appropriately to view the scene elements (e.g., looking along the negative Z-axis). Set its projection to Orthogonal for a 2D-like view. Adjust its `size` property to frame the content correctly.
*   **Background:** Set the project's default clear color (Rendering -> Environment -> Default Clear Color) to Indigo (`#4B0082`).

## 3. Text Elements

*   **Title:**
    *   Add a `Label3D` node.
    *   Text: "Arrow Tips Showcase"
    *   Font: Use the default font or import a clean sans-serif font if desired.
    *   Font Size: Approximately 36.
    *   Color: White (`#FFFFFF`).
    *   Position: Use `Vector3` coordinates. Place it centered horizontally (X=0), near the top (positive Y), and slightly in front of other elements (small negative Z if needed, or ensure it's not occluded).
*   **Subtitle:**
    *   Add a `Label3D` node.
    *   Text: "Axes with different tip styles"
    *   Font: Same as title.
    *   Font Size: Approximately 20.
    *   Color: Yellow (`#FFFF00`).
    *   Position: Use `Vector3` coordinates. Place it centered horizontally (X=0), directly below the Title label (adjust Y), and at a similar Z depth.

## 4. Axes and Arrow Tips Display

*   **Layout:** Arrange 7 examples in a grid: 4 in the first row, 3 in the second row, centered horizontally overall.
*   **Styles to Implement:**
    1.  `ArrowTriangleTip` (Outline Triangle)
    2.  `ArrowTriangleFilledTip` (Filled Triangle)
    3.  `ArrowSquareTip` (Outline Square)
    4.  `ArrowSquareFilledTip` (Filled Square)
    5.  `ArrowCircleTip` (Outline Circle)
    6.  `ArrowCircleFilledTip` (Filled Circle)
    7.  `StealthTip` (Filled, distinct shape)
*   **Structure for Each Example:**
    *   Create a container `Node3D` for each of the 7 examples to group its elements and simplify positioning.
    *   **Axes Lines:**
        *   Use `ImmediateMesh` or thin `CSGBox3D` nodes to draw a horizontal and a vertical line segment, intersecting at their centers. Place them on the XY plane (Z=0 within the container).
        *   Color: White (`#FFFFFF`) using a `StandardMaterial3D` with `albedo_color`.
        *   Thickness: Choose a suitable thickness (e.g., 0.02 units if using CSGBox3D, or set line width if using ImmediateMesh).
        *   Length: Make them relatively short (e.g., 1.5-2.0 units).
    *   **Tick Marks:**
        *   Use `ImmediateMesh` or thin `CSGBox3D` nodes to draw small perpendicular tick marks at the negative ends of the axes lines (on the XY plane).
        *   Color: White (`#FFFFFF`).
        *   Thickness: Same as axes lines.
    *   **Arrow Tips:**
        *   Draw the corresponding arrow tip shape at the positive end of the horizontal axis and the positive end of the vertical axis (on the XY plane).
        *   **Outline Shapes (Triangle, Square, Circle):** Use `ImmediateMesh` nodes, defining the vertices (`Vector3`) to form the closed outline on the XY plane. Set line color to White.
        *   **Filled Shapes (Triangle, Square, Circle, Stealth):** Use `CSGPolygon3D` nodes. Define the 2D vertices of the polygon and set `mode` to `MODE_DEPTH` with a very small `depth` (e.g., 0.01) to give it minimal thickness, or use `ImmediateMesh` to draw filled triangles. Set the material color to White (`#FFFFFF`).
        *   Size the tips appropriately relative to the axis line thickness/length.
    *   **Label:**
        *   Add a `Label3D` node above each axes example.
        *   Text: The corresponding style name (e.g., "ArrowTriangleTip").
        *   Font: Same as title/subtitle.
        *   Font Size: Approximately 24.
        *   Color: White (`#FFFFFF`).
        *   Position: Use `Vector3` coordinates. Place it centered horizontally above its axes representation.

## 5. Implementation Notes

*   A script attached to the root `Node3D` can programmatically create and position all elements in the `_ready()` function.
*   Define helper functions or data structures to manage the points/vertices required for each arrow tip style to avoid repetitive code. Use `Vector3` for positions and vertices, keeping Z=0 for 2D shapes in 3D space.
*   Calculate the `Vector3` positions for each of the 7 example containers based on the desired grid layout and spacing (primarily adjusting X and Y coordinates). Ensure adequate padding between elements and from the scene edges/titles.
*   Ensure all visual elements (lines, shapes, labels) are placed on a plane (e.g., Z=0) that faces the Orthogonal `Camera3D`.
*   Adjust sizes, line thicknesses, positions, and `Camera3D` `size` iteratively to match the reference image `examples/ArrowTips/ArrowTips.png` as closely as possible.
