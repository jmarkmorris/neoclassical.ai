extends Node3D

# Step 1.4: Define Colors
const INDIGO = Color("#4B0082")
const ELECTRIC_PURPLE = Color("#8F00FF")
const PURE_BLUE = Color.BLUE
const PURE_RED = Color.RED
const WHITE = Color.WHITE

# Step 2.2: Coordinate Mapping Variables & Constants
# Manim grid dimensions (inclusive ranges for iteration)
const MANIM_X_MIN = -7
const MANIM_X_MAX = 7  # Note: Manim range(-7, 7) goes up to 6
const MANIM_Y_MIN = -4 # Note: Manim range(4, -4, -1) goes down to -3
const MANIM_Y_MAX = 4
const MANIM_WIDTH_UNITS = float(MANIM_X_MAX - MANIM_X_MIN) # Width covered by cells
const MANIM_HEIGHT_UNITS = float(MANIM_Y_MAX - MANIM_Y_MIN) # Height covered by cells

# Grid line parameters
const GRID_LINE_THICKNESS = 0.02
# Grid lines will be at integer coordinates
const GRID_X_START = float(MANIM_X_MIN)
const GRID_X_END = float(MANIM_X_MAX)
const GRID_Y_START = float(MANIM_Y_MIN)
const GRID_Y_END = float(MANIM_Y_MAX)
const GRID_WIDTH_WORLD = GRID_X_END - GRID_X_START # Total span for horizontal lines
const GRID_HEIGHT_WORLD = GRID_Y_END - GRID_Y_START # Total span for vertical lines

# Cell instantiation parameters (from Step 5)
const RADIUS_START = 0.002
const RADIUS_INCREMENT = 0.002
# Preload Cell Scene (adjust path if needed)
const CircleCell = preload("res://CircleCell.tscn")

# Node references
@onready var grid_container = $GridContainer # Assumes a Node3D named GridContainer exists
@onready var cell_container = $CellContainer # Assumes a Node3D named CellContainer exists


func _ready():
	_create_grid()
	_create_cells()


# Step 3: Create the Grid using MeshInstances
func _create_grid():
	# Material for grid lines
	var grid_material = StandardMaterial3D.new()
	grid_material.albedo_color = ELECTRIC_PURPLE
	grid_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED

	# Vertical lines (at x = -7, -6, ..., 7)
	for i in range(MANIM_X_MIN, MANIM_X_MAX + 1): # Iterate through integer coordinates
		var x_pos = float(i) # Position lines at integers
		var line = MeshInstance3D.new()
		var mesh = CylinderMesh.new()
		mesh.top_radius = GRID_LINE_THICKNESS / 2.0
		mesh.bottom_radius = GRID_LINE_THICKNESS / 2.0
		mesh.height = GRID_HEIGHT_WORLD # Height spans the full Y range
		line.mesh = mesh
		line.material_override = grid_material
		# Position cylinder center: x=x_pos, y=center_of_grid_height
		line.position = Vector3(x_pos, (GRID_Y_START + GRID_Y_END) / 2.0, 0)
		grid_container.add_child(line)

	# Horizontal lines (at y = -4, -3, ..., 4)
	for i in range(MANIM_Y_MIN, MANIM_Y_MAX + 1): # Iterate through integer coordinates
		var y_pos = float(i) # Position lines at integers
		var line = MeshInstance3D.new()
		var mesh = CylinderMesh.new()
		mesh.top_radius = GRID_LINE_THICKNESS / 2.0
		mesh.bottom_radius = GRID_LINE_THICKNESS / 2.0
		mesh.height = GRID_WIDTH_WORLD # Height spans the full X range (before rotation)
		line.mesh = mesh
		line.material_override = grid_material
		# Rotate 90 deg around Z to make it horizontal
		line.rotation_degrees = Vector3(0, 0, 90)
		# Position cylinder center: x=center_of_grid_width, y=y_pos
		line.position = Vector3((GRID_X_START + GRID_X_END) / 2.0, y_pos, 0)
		grid_container.add_child(line)


# Step 5: Instantiate and Position Cells
func _create_cells():
	var current_radius = RADIUS_START

	# Manim loops from y=4 down to y=-3, and x=-7 to x=6
	# Manim loops from y=4 down to y=-3 (inclusive), and x=-7 to x=6 (inclusive).
	# Godot range(start, end, step) stops *before* end.
	# For y: range(4, -4, -1) yields 4, 3, 2, 1, 0, -1, -2, -3.
	# For x: range(-7, 7) yields -7, -6, ..., 5, 6.
	for y_manim in range(MANIM_Y_MAX, MANIM_Y_MIN, -1): # Corrected range: 4 down to -3
		for x_manim in range(MANIM_X_MIN, MANIM_X_MAX): # Correct range: -7 to 6
			# Instantiate cell
			var cell_instance = CircleCell.instantiate()

			# Configure cell (update_display should be defined in CircleCell.gd)
			if cell_instance.has_method("update_display"):
				cell_instance.update_display(current_radius)
			else:
				push_warning("CircleCell scene is missing update_display method.")

			# Position the cell instance at the Manim grid point (center)
			cell_instance.position = Vector3(float(x_manim), float(y_manim), 0.0)

			# Add to scene tree under the container
			cell_container.add_child(cell_instance)

			# Increment radius
			current_radius += RADIUS_INCREMENT

# Removed map_manim_to_godot as direct mapping is used for cells
# and grid lines are calculated directly.
