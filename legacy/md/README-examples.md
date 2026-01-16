# Visualization Examples

## Project Overview

This project is a comprehensive collection of Godot Engine and Manim (Mathematical Animation Engine) examples designed to showcase the powerful visualization and animation capabilities of the Manim library. Each script demonstrates different aspects of mathematical, scientific, and programmatic visualization techniques. Examples may be implemented in Godot engine or Manim or both.

## Run Tool Script

`run_example.sh` is an interactive bash script that provides a user-friendly interface to explore and run the Manim examples. Key features include:
- Dynamic listing of available Python visualization scripts
- Numbered menu for easy selection
- High-quality rendering with preview
- Help and navigation options
- Automatic handling of script execution from the project root

## Example Descriptions

### 1. AngleClassUse.py
A comprehensive demonstration of advanced angle visualization using a custom `AngleGroup` class. This example showcases:
- Dynamic angle transformations with smooth updaters
- Interactive scaling of angle groups
- Pause and resume functionality for animations
- Multiple angle groups with independent behaviors
- Random color generation for visual diversity
- Complex path-following animations

### 2. AnimatedAngle.py
An exploration of angle rotation with dynamic visual properties:
- Randomized color generation for lines, arcs, and labels using the shared `AngleGroup`
- Smooth rotation simulated using `UpdateFromAlphaFunc` on `AngleGroup`
- Demonstration of `AngleGroup` instantiation and color setting
- Showcasing Manim's flexibility in geometric animations via `AngleGroup`

### 3. AnglePath.py
An advanced visualization of angle movement along a complex parametric path using the shared `AngleGroup`:
- Parametric curve generation using trigonometric functions
- Dynamic angle updates handled by `AngleGroup` based on path progression
- Handling of degenerate angle cases within `AngleGroup`
- Smooth angle and label positioning managed by `AngleGroup`
- Exploration of non-linear path following with `AngleGroup`

### 4. ArrowTips.py
A comprehensive showcase of Manim's arrow tip styles:
- Display of multiple arrow tip variations
- Comparison of filled and outlined tip styles
- Demonstration of different geometric tip shapes
- Systematic layout of arrow tip examples

### 5. CircleSizes.py
A precise visualization of circle scaling and size variations:
- Incremental radius changes
- Grid-based circle rendering
- Demonstration of opacity and size control
- Systematic exploration of geometric scaling

### 6. Clock.py
A dynamic, real-time clock visualization:
- Accurate time representation
- Smooth hand movements
- Path-following animation
- Real-time updaters for hour, minute, and second hands
- Demonstration of complex time-based animations

### 7. Dot3DGrid.py
An in-depth exploration of 3D sphere rendering:
- Comprehensive display of sphere rendering options
- Variations in sheen, ambient, and specular properties
- 3D camera rotation and lighting effects
- Systematic comparison of sphere rendering parameters

### 8. LatexPlus.py
A rich demonstration of LaTeX and text manipulation:
- LaTeX and text rendering
- Dynamic text transformations
- Background and grid manipulations
- Showcasing Manim's text and mathematical notation capabilities

### 9. LineOpacity.py
A detailed visualization of line opacity and stroke width:
- Systematic display of opacity variations
- Multiple stroke width demonstrations
- Precise control of line visual properties
- Clear representation of opacity effects

### 10. Lorenz3D.py
A mesmerizing visualization of the Lorenz attractor:
- 3D rendering of the Lorenz dynamical system
- Parametric trajectory generation
- Dot tracking along the complex attractor path
- Demonstration of scientific visualization techniques

### 11. MakeGraph.py
A comprehensive function graphing example:
- Multiple function plotting
- Axis configuration and labeling
- Graph styling and customization
- Demonstration of mathematical function visualization

### 12. MovingFrameBox.py
An interactive demonstration of frame box animations:
- Dynamic highlighting of mathematical expressions
- Smooth frame box transformations
- Showcasing text and equation visualization techniques

### 13. MultipleAnimations.py
A complex, multi-layered animation example:
- Concurrent animations with different behaviors
- Text typing and object rotation
- Updater-based dynamic effects
- Demonstration of Manim's animation composition

### 14. PathTrace.py
An exploration of path tracing and dot movement:
- Random trajectory generation
- Dynamic path creation
- Dot movement along complex paths
- Visualization of motion and trajectory

### 15. PointMovingOnShapes.py
A versatile demonstration of point movement:
- Movement along various geometric shapes
- Different rate functions and animation styles
- Systematic exploration of motion techniques
- Showcasing Manim's animation flexibility

### 16. PolarCoordinates.py
A detailed visualization of polar coordinate systems:
- Polar plane rendering
- Vector representation in polar coordinates
- Axis and label configuration
- Demonstration of coordinate system visualization

### 17. Square.py
A configurable scene that tiles the Manim frame with colored squares:
- Loads configuration (size, color scheme, borders, opacity) from `examples/Square.json`
- Supports multiple color schemes (alternating, random, etc.)
- Allows enabling/disabling borders and opacity variation
- Demonstrates loading external configuration and grid-based layouts

### 18. TextFontsSizes.py
A comprehensive text rendering showcase:
- Exploration of font variations
- Size and weight demonstrations
- Text styling and formatting
- Systematic display of text rendering capabilities

### 19. UpdatersExample.py
An advanced demonstration of Manim's updater functionality:
- Multiple interactive objects with dynamic behaviors
- Complex updater interactions
- Real-time object transformations
- Showcasing the power of Manim's updater system

### 20. VectorArrow.py
A precise vector and coordinate visualization:
- Vector arrow creation and placement
- Number plane rendering
- Coordinate system labeling
- Demonstration of vector visualization techniques

### 21. WriteStuff.py
A basic introduction to Manim's text and animation capabilities:
- Text and LaTeX writing animations
- Simple text transformations
- Demonstration of basic Manim animation techniques

## Rendering Notes
- Some examples generate static images
- Most examples create animated videos
- Rendering quality can be adjusted in the Manim configuration

## Getting Started
1. Ensure Manim is installed
2. Navigate to the project root
3. Use `./examples/run_example.sh` to explore and run examples
```
