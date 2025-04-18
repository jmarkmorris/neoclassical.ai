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

	# --- Create Shaft ---
	var shaft_mesh = CylinderMesh.new()
	shaft_mesh.top_radius = ARROW_SHAFT_RADIUS
	shaft_mesh.bottom_radius = ARROW_SHAFT_RADIUS
	# Adjust height slightly to prevent Z-fighting with the tip base
	shaft_mesh.height = length - ARROW_TIP_HEIGHT * 0.95

	var shaft_instance = MeshInstance3D.new()
	shaft_instance.mesh = shaft_mesh
	shaft_instance.material_override = material # Use material_override
	shaft_instance.name = "Shaft"

	# Position and orient the shaft
	# CylinderMesh is oriented along Y-axis by default
	# We need to rotate it to align with the direction vector
	# Then position its center between start and (end - tip_height)
	var shaft_center = start_point + direction.normalized() * (shaft_mesh.height / 2.0)
	shaft_instance.global_position = shaft_center
	# Align the cylinder's Y-axis with the arrow's direction
	shaft_instance.look_at(end_point, Vector3.UP)
	# CylinderMesh points along +Y, look_at points along -Z. Rotate to fix.
	shaft_instance.rotate_object_local(Vector3.RIGHT, PI / 2)

	arrow_node.add_child(shaft_instance)

	# --- Create Tip (using PrismMesh as workaround for ConeMesh issue) ---
	var tip_mesh = PrismMesh.new()
	# Make it a pyramid (pointy top)
	tip_mesh.left_to_right = 0
	# Set base size (X and Z) and height (Y)
	tip_mesh.size = Vector3(ARROW_TIP_RADIUS * 2, ARROW_TIP_HEIGHT, ARROW_TIP_RADIUS * 2)

	var tip_instance = MeshInstance3D.new()
	tip_instance.mesh = tip_mesh
	tip_instance.material_override = material # Use material_override
	tip_instance.name = "Tip"

	# Position and orient the tip
	# ConeMesh is oriented along Y-axis by default, base at Y=0
	# Position the base of the cone at the end point
	# Align the cone's Y-axis with the arrow's direction
	var tip_base_position = end_point - direction.normalized() * ARROW_TIP_HEIGHT
	tip_instance.global_position = tip_base_position + direction.normalized() * (ARROW_TIP_HEIGHT / 2.0)
	tip_instance.look_at(end_point + direction.normalized(), Vector3.UP) # Look slightly past the end point
	# ConeMesh points along +Y, look_at points along -Z. Rotate to fix.
	tip_instance.rotate_object_local(Vector3.RIGHT, PI / 2)

	arrow_node.add_child(tip_instance)
