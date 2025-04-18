@tool # Add tool mode annotation as a diagnostic step
extends Node3D

# Grid configuration
const GRID_SIZE = 10.0  # Extends from -GRID_SIZE to +GRID_SIZE
const GRID_SPACING = 1.0
const GRID_COLOR = Color(0, 0.7, 1.0) # Cyan/Blue color similar to reference
const GRID_LINE_WIDTH = 2.0 # Approximate line width

# Camera configuration (basic for now)
const CAMERA_DISTANCE = 20.0

# Arrow configuration
const ARROW_START = Vector3.ZERO
const ARROW_END = Vector3(2, 2, 0)
const ARROW_COLOR = Color.WHITE
const ARROW_SHAFT_RADIUS = 0.05
const ARROW_TIP_HEIGHT = 0.3
const ARROW_TIP_RADIUS = 0.15

# Called when the node enters the scene tree for the first time.
func _ready():
	_create_grid()
	_setup_basic_camera()
	_create_vector_arrow(ARROW_START, ARROW_END)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

# Creates the grid background using ImmediateMesh
func _create_grid():
	var grid_node = Node3D.new()
	grid_node.name = "Grid"
	add_child(grid_node)

	var immediate_mesh = ImmediateMesh.new()
	var material = StandardMaterial3D.new()
	material.albedo_color = GRID_COLOR
	material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED # Make color flat

	immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINES, material)

	# Vertical lines
	for i in range(-int(GRID_SIZE / GRID_SPACING), int(GRID_SIZE / GRID_SPACING) + 1):
		var x = i * GRID_SPACING
		immediate_mesh.surface_add_vertex(Vector3(x, -GRID_SIZE, 0))
		immediate_mesh.surface_add_vertex(Vector3(x, GRID_SIZE, 0))

	# Horizontal lines
	for i in range(-int(GRID_SIZE / GRID_SPACING), int(GRID_SIZE / GRID_SPACING) + 1):
		var y = i * GRID_SPACING
		immediate_mesh.surface_add_vertex(Vector3(-GRID_SIZE, y, 0))
		immediate_mesh.surface_add_vertex(Vector3(GRID_SIZE, y, 0))

	immediate_mesh.surface_end()

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = immediate_mesh
	# Note: Setting line width directly isn't standard for ImmediateMesh lines.
	# The visual width depends on resolution and distance.
	# For thicker lines, consider using TubeTrailMesh or custom shaders.
	grid_node.add_child(mesh_instance)

# Sets up a basic camera to view the scene
func _setup_basic_camera():
	var camera = Camera3D.new()
	camera.position = Vector3(0, 0, CAMERA_DISTANCE) # Position camera back along Z-axis
	camera.look_at(Vector3.ZERO) # Make camera look at the origin
	add_child(camera)

# Creates a 3D arrow from start_point to end_point
func _create_vector_arrow(start_point: Vector3, end_point: Vector3):
	var arrow_node = Node3D.new()
	arrow_node.name = "VectorArrow"
	add_child(arrow_node)

	var direction = end_point - start_point
	var length = direction.length()

	if length < 0.001: # Avoid issues with zero-length vectors
		printerr("Arrow length is too small.")
		return

	# --- Create Material ---
	var material = StandardMaterial3D.new()
	material.albedo_color = ARROW_COLOR
	material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED

	# Position and orient the main arrow container
	arrow_node.position = start_point
	arrow_node.look_at(end_point, Vector3.UP) # Point container's -Z towards end_point

	# --- Create Shaft ---
	var shaft_length = length - ARROW_TIP_HEIGHT # Calculate actual shaft length
	if shaft_length < 0: shaft_length = 0 # Ensure non-negative length

	var shaft_mesh = CylinderMesh.new()
	shaft_mesh.top_radius = ARROW_SHAFT_RADIUS
	shaft_mesh.bottom_radius = ARROW_SHAFT_RADIUS
	shaft_mesh.height = shaft_length

	var shaft_instance = MeshInstance3D.new()
	shaft_instance.mesh = shaft_mesh
	shaft_instance.material_override = material
	shaft_instance.name = "Shaft"

	# Position and orient the shaft *locally* within the arrow_node
	# Rotate Cylinder's Y-axis to align with parent's -Z axis
	shaft_instance.rotation.x = PI / 2
	# Position center of shaft along parent's -Z axis
	shaft_instance.position.z = -shaft_length / 2.0
	arrow_node.add_child(shaft_instance)

	# --- Create Tip (using PrismMesh as workaround) ---
	var tip_mesh = PrismMesh.new()
	tip_mesh.left_to_right = 0 # Make it a pyramid
	# Size: X=width, Y=height, Z=depth. We want height along arrow direction.
	tip_mesh.size = Vector3(ARROW_TIP_RADIUS * 2, ARROW_TIP_HEIGHT, ARROW_TIP_RADIUS * 2)

	var tip_instance = MeshInstance3D.new()
	tip_instance.mesh = tip_mesh
	tip_instance.material_override = material
	tip_instance.name = "Tip"

	# Position and orient the tip *locally* within the arrow_node
	# Rotate Prism's Y-axis (height) to align with parent's -Z axis
	tip_instance.rotation.x = PI / 2
	# Position center of tip along parent's -Z axis, at the end of the shaft
	tip_instance.position.z = -shaft_length - (ARROW_TIP_HEIGHT / 2.0)
	arrow_node.add_child(tip_instance)
