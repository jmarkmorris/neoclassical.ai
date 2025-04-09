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

# Materials
var white_material: StandardMaterial3D
var vector_material: StandardMaterial3D

# Called when the node enters the scene tree for the first time.
func _ready():
	# Clear previous children if any (useful for @tool script reloading)
	for child in get_children():
		child.queue_free()
		
	_initialize_materials()
	_create_circles()
	_create_radial_lines()
	_create_labels()
	_create_vector()

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
func _create_circles():
	for r in RADII:
		var im := ImmediateMesh.new()
		var mi := MeshInstance3D.new()
		mi.mesh = im
		mi.material_override = white_material
		add_child(mi)

		im.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
		for i in range(CIRCLE_SEGMENTS + 1):
			var angle = float(i) / CIRCLE_SEGMENTS * TAU # TAU is 2*PI
			im.surface_add_vertex(_polar_to_cartesian(r, angle))
		im.surface_end()

# Create radial lines using ImmediateMesh
func _create_radial_lines():
	for i in range(NUM_RADIAL_LINES):
		var angle = float(i) / NUM_RADIAL_LINES * TAU
		var end_point = _polar_to_cartesian(MAX_RADIUS, angle)
		
		var im := ImmediateMesh.new()
		var mi := MeshInstance3D.new()
		mi.mesh = im
		mi.material_override = white_material
		add_child(mi)

		im.surface_begin(Mesh.PRIMITIVE_LINES)
		im.surface_add_vertex(Vector3.ZERO) # Start at origin
		im.surface_add_vertex(end_point)   # End at max radius
		im.surface_end()

# Create Label3D nodes for radius and azimuth markers
func _create_labels():
	# Radius Labels (along positive X axis)
	for r in RADII:
		var label_pos = Vector3(r, -LABEL_OFFSET, 0) # Position slightly below the axis
		var label_text = str(snapped(r, 0.1)) # Format to one decimal place
		add_child(_create_label(label_text, label_pos))

	# Azimuth Labels (around the perimeter)
	var azimuth_texts = ["0", "π/6", "π/3", "π/2", "2π/3", "5π/6", "π", "7π/6", "4π/3", "3π/2", "5π/3", "11π/6"]
	for i in range(NUM_RADIAL_LINES):
		var angle = float(i) / NUM_RADIAL_LINES * TAU
		# Place label slightly outside the max radius
		var label_pos = _polar_to_cartesian(MAX_RADIUS + LABEL_OFFSET, angle)
		add_child(_create_label(azimuth_texts[i], label_pos))

# Helper function to create and configure a Label3D
func _create_label(text: String, position: Vector3) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = LABEL_FONT_SIZE
	label.pixel_size = LABEL_PIXEL_SIZE
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.shading_mode = Label3D.SHADING_MODE_UNSHADED
	label.modulate = WHITE_COLOR # Use modulate for color
	label.transform.origin = position
	# Center align text horizontally and vertically
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return label

# Create the vector arrow (line + arrowhead)
func _create_vector():
	var vector_end_point = _polar_to_cartesian(VECTOR_R, VECTOR_THETA)
	
	# Use CylinderMesh for the line part to give it thickness
	var line := MeshInstance3D.new()
	var line_mesh := CylinderMesh.new()
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
	
	add_child(line)

	# Use ConeMesh for the arrowhead
	var arrowhead := MeshInstance3D.new()
	var arrowhead_mesh := ConeMesh.new()
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

	add_child(arrowhead)
