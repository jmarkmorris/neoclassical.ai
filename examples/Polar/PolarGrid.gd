@tool
extends Node3D

# Configuration constants based on design.md and reference image/script
const WHITE_COLOR := Color(1.0, 1.0, 1.0)
# Match Manim RED_E (#FC6255), closest is maybe a lighter red/orange
const VECTOR_COLOR := Color(1.0, 0.38, 0.33) 
const RADII := [1.0, 2.0, 3.0, 4.0]
const MAX_RADIUS := 4.0
const NUM_RADIAL_LINES := 12
const LABEL_OFFSET := 0.3 # Distance labels are placed outside the max radius
const LABEL_FONT_SIZE := 64 # Adjust for visual clarity
const LABEL_PIXEL_SIZE := 0.005 # Adjust for visual clarity

const VECTOR_R := 2.4
const VECTOR_THETA := PI / 4.0
const VECTOR_LINE_WIDTH := 0.03 # Visual thickness for the vector line
const ARROWHEAD_HEIGHT := 0.2
const ARROWHEAD_RADIUS := 0.1

const CIRCLE_SEGMENTS := 64 # Number of segments for drawing circles

# Node references (optional, could also find_child)
var camera: Camera3D
var title_label: Label3D
var grid_container: Node3D

# Materials
var white_material: StandardMaterial3D
var vector_material: StandardMaterial3D

# Called when the node enters the scene tree for the first time.
# In @tool mode, this also runs in the editor.
func _ready():
	# Clear previous children if any (useful for @tool script reloading)
	# Use call_deferred to avoid issues during editor initialization/reloading
	call_deferred("_clear_children_and_rebuild")

func _clear_children_and_rebuild():
	# Clear previous children safely
	for child in get_children():
		child.queue_free()

	# Create and configure Camera
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	# Adjust size to fit the grid (max radius 4) plus some padding
	camera.size = (MAX_RADIUS + LABEL_OFFSET + 0.5) * 2 
	# Position camera to view the XY plane from the front
	camera.transform.origin = Vector3(0, 0, 10) 
	camera.current = true
	add_child(camera)

	# Create and configure Title Label
	title_label = _create_label("Polar Coordinates Visualization", Vector3.ZERO) # Position set below
	# Position title above the grid area
	title_label.transform.origin = Vector3(0, MAX_RADIUS + 1.5, 0) 
	add_child(title_label)

	# Create container for grid elements
	grid_container = Node3D.new()
	grid_container.name = "GridContainer"
	# Position grid container slightly below center as per design.md
	grid_container.position = Vector3(0, -0.5, 0) 
	add_child(grid_container)
		
	_initialize_materials()
	# Pass the container to the creation functions
	_create_circles(grid_container)
	_create_radial_lines(grid_container)
	_create_labels(grid_container)
	_create_vector(grid_container)

# Initialize unshaded materials
func _initialize_materials():
	white_material = StandardMaterial3D.new()
	white_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	white_material.albedo_color = WHITE_COLOR

	vector_material = StandardMaterial3D.new()
	vector_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	vector_material.albedo_color = VECTOR_COLOR

# Helper to convert polar coordinates to Cartesian Vector3 (on XY plane)
func _polar_to_cartesian(r: float, theta: float) -> Vector3:
	return Vector3(r * cos(theta), r * sin(theta), 0)

# Create concentric circles using ImmediateMesh
func _create_circles(parent_node: Node3D):
	for r in RADII:
		var im := ImmediateMesh.new()
		var mi := MeshInstance3D.new()
		mi.name = "Circle_r" + str(r)
		mi.mesh = im
		mi.material_override = white_material
		parent_node.add_child(mi)

		im.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
		for i in range(CIRCLE_SEGMENTS + 1):
			var angle = float(i) / CIRCLE_SEGMENTS * TAU # TAU is 2*PI
			im.surface_add_vertex(_polar_to_cartesian(r, angle))
		im.surface_end()

# Create radial lines using ImmediateMesh
func _create_radial_lines(parent_node: Node3D):
	for i in range(NUM_RADIAL_LINES):
		var angle = float(i) / NUM_RADIAL_LINES * TAU
		var end_point = _polar_to_cartesian(MAX_RADIUS, angle)
		
		var im := ImmediateMesh.new()
		var mi := MeshInstance3D.new()
		mi.name = "RadialLine_" + str(i)
		mi.mesh = im
		mi.material_override = white_material
		parent_node.add_child(mi)

		im.surface_begin(Mesh.PRIMITIVE_LINES)
		im.surface_add_vertex(Vector3.ZERO) # Start at origin
		im.surface_add_vertex(end_point)   # End at max radius
		im.surface_end()

# Create Label3D nodes for radius and azimuth markers
func _create_labels(parent_node: Node3D):
	# Radius Labels (along positive X axis)
	for r in RADII:
		var label_pos = Vector3(r, -LABEL_OFFSET, 0) # Position slightly below the axis
		var label_text = str(snapped(r, 0.1)) # Format to one decimal place
		var radius_label = _create_label(label_text, label_pos)
		radius_label.name = "RadiusLabel_" + str(r)
		parent_node.add_child(radius_label)

	# Azimuth Labels (around the perimeter)
	var azimuth_texts = ["0", "π/6", "π/3", "π/2", "2π/3", "5π/6", "π", "7π/6", "4π/3", "3π/2", "5π/3", "11π/6"]
	for i in range(NUM_RADIAL_LINES):
		var angle = float(i) / NUM_RADIAL_LINES * TAU
		# Place label slightly outside the max radius
		var label_pos = _polar_to_cartesian(MAX_RADIUS + LABEL_OFFSET, angle)
		var azimuth_label = _create_label(azimuth_texts[i], label_pos)
		azimuth_label.name = "AzimuthLabel_" + str(i)
		parent_node.add_child(azimuth_label)


# Helper function to create and configure a Label3D
# Note: This helper now only configures the label, positioning is handled by the caller
func _create_label(text: String, position: Vector3) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = LABEL_FONT_SIZE
	label.pixel_size = LABEL_PIXEL_SIZE
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true # Use no_depth_test instead of shading_mode
	label.modulate = WHITE_COLOR # Use modulate for color
	label.transform.origin = position # Set initial position
	# Center align text horizontally and vertically
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return label

# Create the vector arrow (line + arrowhead)
func _create_vector(parent_node: Node3D):
	var vector_end_point = _polar_to_cartesian(VECTOR_R, VECTOR_THETA)
	
	# Use CylinderMesh for the line part to give it thickness
	var line := MeshInstance3D.new()
	line.name = "VectorLine"
	# Use ClassDB to instantiate in case of parser issues with direct type name
	var line_mesh = ClassDB.instantiate("CylinderMesh") 
	if line_mesh == null: # Check if instantiation failed
		push_error("Failed to instantiate CylinderMesh using ClassDB")
		return # Avoid further errors
	line_mesh.top_radius = VECTOR_LINE_WIDTH / 2.0
	line_mesh.bottom_radius = VECTOR_LINE_WIDTH / 2.0
	line_mesh.height = vector_end_point.length() # Length of the vector
	line.mesh = line_mesh
	line.material_override = vector_material
	
	# Position the cylinder center at half the vector length along its direction
	# and rotate it to align with the vector direction
	line.transform.origin = vector_end_point / 2.0 
	# Align the cylinder's Y-axis (height) with the vector direction
	line.look_at(vector_end_point, Vector3.UP) 
	# Cylinder points along its +Y axis by default, look_at points -Z. Rotate to fix.
	line.rotate_object_local(Vector3.RIGHT, PI / 2.0)
	
	parent_node.add_child(line)

	# Use ConeMesh for the arrowhead
	var arrowhead := MeshInstance3D.new()
	arrowhead.name = "VectorArrowhead"
	# Use ClassDB to instantiate in case of parser issues with direct type name
	var arrowhead_mesh = ClassDB.instantiate("ConeMesh")
	if arrowhead_mesh == null: # Check if instantiation failed
		push_error("Failed to instantiate ConeMesh using ClassDB")
		return # Avoid further errors
	arrowhead_mesh.radius = ARROWHEAD_RADIUS
	arrowhead_mesh.height = ARROWHEAD_HEIGHT
	arrowhead.mesh = arrowhead_mesh
	arrowhead.material_override = vector_material

	# Position the base of the cone at the vector's end point
	# Rotate it to point in the vector's direction
	arrowhead.transform.origin = vector_end_point
	# Align the cone's Y-axis (height) with the vector direction
	arrowhead.look_at(vector_end_point + vector_end_point.normalized() * ARROWHEAD_HEIGHT, Vector3.UP)
	# Cone points along its +Y axis by default, look_at points -Z. Rotate to fix.
	arrowhead.rotate_object_local(Vector3.RIGHT, PI / 2.0)

	parent_node.add_child(arrowhead)
