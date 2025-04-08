extends Node3D

# Step 1.4: Define Colors
const INDIGO = Color("#4B0082")
const ELECTRIC_PURPLE = Color("#8F00FF")
const PURE_BLUE = Color.BLUE
const PURE_RED = Color.RED
const WHITE = Color.WHITE

# Grid Definition Variables & Constants
# Grid dimensions (world units, inclusive ranges for iteration)
const GRID_X_MIN = -7
const GRID_X_MAX = 7
const GRID_Y_MIN = -4
const GRID_Y_MAX = 4
const GRID_WIDTH_UNITS = float(GRID_X_MAX - GRID_X_MIN) # Width covered by cells
const GRID_HEIGHT_UNITS = float(GRID_Y_MAX - GRID_Y_MIN) # Height covered by cells

# Grid line parameters
const GRID_LINE_THICKNESS = 0.02
# Grid lines will be at integer coordinates
const GRID_X_START = float(GRID_X_MIN)
const GRID_X_END = float(GRID_X_MAX)
const GRID_Y_START = float(GRID_Y_MIN)
const GRID_Y_END = float(GRID_Y_MAX)
const GRID_WIDTH_WORLD = GRID_X_END - GRID_X_START # Total span for horizontal lines
const GRID_HEIGHT_WORLD = GRID_Y_END - GRID_Y_START # Total span for vertical lines

# Cell instantiation parameters
const RADIUS_START = 0.002
const RADIUS_INCREMENT = 0.002
# Preload Cell Scene
const CircleCell = preload("res://CircleCell.tscn")

# Node references
@onready var grid_container = $GridContainer # Assumes a Node3D named GridContainer exists
@onready var cell_container = $CellContainer # Assumes a Node3D named CellContainer exists


func _ready():
	_create_grid()
	_create_cells()


# Create the Grid using MeshInstances
func _create_grid():
	# Material for grid lines
	var grid_material = StandardMaterial3D.new()
	grid_material.albedo_color = ELECTRIC_PURPLE
	grid_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED

	# Vertical lines (at x = -7, -6, ..., 7)
	for i in range(GRID_X_MIN, GRID_X_MAX + 1): # Iterate through integer coordinates
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
	for i in range(GRID_Y_MIN, GRID_Y_MAX + 1): # Iterate through integer coordinates
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


# Instantiate and Position Cells
func _create_cells():
	var current_radius = RADIUS_START

	# Iterate through grid cells top-to-bottom (y descending), then left-to-right (x ascending).
	# This specific order is required to assign radii sequentially, increasing from top-left to bottom-right.
	# Y range: GRID_Y_MAX down to GRID_Y_MIN + 1 (e.g., 4 down to -3)
	# X range: GRID_X_MIN up to GRID_X_MAX - 1 (e.g., -7 up to 6)
	for grid_y in range(GRID_Y_MAX, GRID_Y_MIN, -1): # Iterate Y downwards
		for grid_x in range(GRID_X_MIN, GRID_X_MAX): # Iterate X upwards
			# Instantiate cell
			var cell_instance = CircleCell.instantiate()

			# Configure cell (update_display should be defined in CircleCell.gd)
			if cell_instance.has_method("update_display"):
				cell_instance.update_display(current_radius)
			else:
				push_warning("CircleCell scene is missing update_display method.")

			# Position the cell instance at the integer grid coordinates
			cell_instance.position = Vector3(float(grid_x), float(grid_y), 0.0)

			# Add to scene tree under the container
			cell_container.add_child(cell_instance)

			# Increment radius
			current_radius += RADIUS_INCREMENT
