# Godot Scene Design: Line Opacity Visualization

This document describes the desired Godot scene based on the provided image (`goal.png`). The goal is to visualize vertical lines with varying opacity and stroke widths.

## 1. Scene Setup

-   **Root Node:** Use a `Node2D` as the main scene root.
-   **Background Color:** Configure the project's default clear color to be the dark purple shown in the image. Use the value `Color(0.294118, 0, 0.509804, 1)` (as found in `project.godot`).

## 2. Text Elements

Create the following text elements using `Label` nodes. Use the default Godot font unless specified otherwise. Set text color to white (`Color(1, 1, 1, 1)`) unless specified otherwise.

### 2.1. Title
-   **Node:** `Label`
-   **Text:** "Line Opacity Visualization (Even % from 0% to 100%)"
-   **Position:** Horizontally centered near the top edge of the viewport. Add appropriate top margin (e.g., 50 pixels).
-   **Styling:** Use a relatively large font size (e.g., 36).

### 2.2. Subtitle
-   **Node:** `Label`
-   **Text:** "Line(start=[x, y, z], end=[x, y, z], stroke_width=w, stroke_opacity=o)"
-   **Color:** Yellow (`Color(1, 1, 0, 1)`).
-   **Position:** Horizontally centered, directly below the Title. Add minor vertical spacing (e.g., 10 pixels) below the title.
-   **Styling:** Use a smaller font size than the title (e.g., 24).

### 2.3. Width Labels
-   Create three separate `Label` nodes, one for each line group.
-   **Text:** "Width: 3", "Width: 2", "Width: 1".
-   **Position:** Place each label immediately to the left of its corresponding line group (see section 3). Vertically align the label with the center of the lines in its group. Add some horizontal padding between the label and the first line (e.g., 20 pixels). Ensure these labels are horizontally aligned with each other (e.g., using the same x-coordinate for their right edge).
-   **Styling:** Use a suitable font size (e.g., 28).

### 2.4. Axis Percentage Labels
-   Create five `Label` nodes.
-   **Text:** "0%", "25%", "50%", "75%", "100%".
-   **Position:** Place each label directly below its corresponding axis tick mark (see section 4). Center the label horizontally under the tick. Add minor vertical spacing below the ticks (e.g., 5 pixels).
-   **Styling:** Use a suitable font size (e.g., 24).

## 3. Line Visualization Groups

Create three distinct groups of lines, arranged vertically.

### 3.1. General Group Layout
-   Define a common horizontal span (width) for the lines within each group (e.g., 800 pixels). Center this span horizontally within the viewport.
-   Define a common vertical size (height) for all lines (e.g., 100 pixels).
-   Arrange the three groups vertically, centered within the available space between the subtitle and the axis labels. Add vertical spacing between each group (e.g., 50 pixels).

### 3.2. Individual Line Group Details (Repeat for Widths 3, 2, 1)
-   For each group:
    -   **Container:** Use a `Node2D` as a container for the group to manage positioning.
    -   **Line Implementation:** Draw the lines within the `_draw()` method of the container `Node2D`. This is preferred over creating many `Line2D` nodes for performance.
    -   **Number of Lines:** Draw 101 vertical lines.
    -   **Stroke Width:** Use the width corresponding to the group: 3 for the top group, 2 for the middle, 1 for the bottom.
    -   **Line Geometry:**
        -   All lines are vertical and have the same height (e.g., `start_y = -50`, `end_y = 50` relative to the container's origin).
        -   Calculate the x-coordinates for the 101 lines to be evenly spaced across the defined horizontal span. The first line (index 0) should be at the leftmost edge of the span, and the last line (index 100) at the rightmost edge.
    -   **Color and Opacity:**
        -   Use white (`Color(1, 1, 1)`) as the base color for the lines.
        -   Vary the alpha component (opacity) linearly across the lines.
        -   The `i`-th line (index `i` from 0 to 100) should have an opacity of `alpha = i / 100.0`.
        -   Pass this calculated color (with varying alpha) to the `draw_line` function.

## 4. Axis Ticks

Create visual markers below the line groups corresponding to specific opacity percentages.

-   **Implementation:** Draw 5 short vertical lines using the `_draw()` method of a dedicated `Node2D` or use individual `Line2D` nodes.
-   **Geometry:** Make the ticks short (e.g., 10 pixels high) and thin (width 1).
-   **Color:** White (`Color(1, 1, 1, 1)`).
-   **Position:**
    -   Place the ticks below the bottom line group, leaving some vertical space.
    -   Horizontally align the ticks with the lines representing 0%, 25%, 50%, 75%, and 100% opacity. Their x-coordinates must match the x-coordinates of the lines with indices 0, 25, 50, 75, and 100 within the line groups above.

## 5. Node Structure Suggestion

Organize the scene using a hierarchy similar to this:

```
- OpacityScene (Node2D)
  - TitleLabel (Label)
  - SubtitleLabel (Label)
  - LineGroupWidth3 (Node2D)  # Draws lines in _draw()
    - LabelWidth3 (Label)
  - LineGroupWidth2 (Node2D)  # Draws lines in _draw()
    - LabelWidth2 (Label)
  - LineGroupWidth1 (Node2D)  # Draws lines in _draw()
    - LabelWidth1 (Label)
  - AxisDisplay (Node2D)      # Draws ticks in _draw()
    - LabelPercent0 (Label)
    - LabelPercent25 (Label)
    - LabelPercent50 (Label)
    - LabelPercent75 (Label)
    - LabelPercent100 (Label)
```

Use positioning properties (e.g., `position`, `offset`, `anchors` if using Control nodes for layout) to arrange the nodes according to the visual requirements. Ensure calculations for line positions and opacities are done accurately within the script attached to the line group nodes.
