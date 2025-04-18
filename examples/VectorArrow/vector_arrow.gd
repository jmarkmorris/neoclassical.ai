extends Node3D

# Grid configuration
const GRID_SIZE = 10.0  # Extends from -GRID_SIZE to +GRID_SIZE
const GRID_SPACING = 1.0
const GRID_COLOR = Color(0, 0.7, 1.0) # Cyan/Blue color similar to reference
const GRID_LINE_WIDTH = 2.0 # Approximate line width

# Camera configuration (basic for now)
const CAMERA_DISTANCE = 20.0

# Called when the node enters the scene tree for the first time.
func _ready():
	_create_grid()
	_setup_basic_camera()


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
