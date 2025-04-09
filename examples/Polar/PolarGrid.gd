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
const LABEL_FONT_SIZE := 128 # Increased for larger title/labels
const LABEL_PIXEL_SIZE := 0.0025 # Decreased for sharper, larger text

const VECTOR_R := 2.4
const VECTOR_THETA := PI / 4.0
# --- Reverted sizes back to smaller values ---
const VECTOR_LINE_WIDTH := 0.03 # Original value
const ARROWHEAD_HEIGHT := 0.2  # Original value
const ARROWHEAD_RADIUS := 0.1  # Original value
# --- End reverted sizes ---

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
	# Adjust size to fit the grid (max radius 4 + offset) and title comfortably
	camera.size = 11.0 # Increased from 9.6 to ensure title and labels fit
	# Position camera to view the XY plane from the front
	camera.transform.origin = Vector3(0, 0, 10) 
	camera.current = true
	add_child(camera)

	# Create and configure Title Label
	title_label = _create_label("Polar Coordinates Visualization", Vector3.ZERO) # Position set below
	# Position title above the grid area, slightly lower than before
	title_label.transform.origin = Vector3(0, MAX_RADIUS + 1.0, 0) # Lowered Y from +1.5 to +1.0
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
	white_material.emission_enabled = true # Enable emission
	white_material.emission = WHITE_COLOR # Add emission for brightness boost

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
		# Increase downward offset to match goal.jpg more closely
		var label_pos = Vector3(r, -LABEL_OFFSET * 2.0, 0) # Position further below the axis
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
	
	# Use ClassDB to instantiate CylinderMesh to avoid parser issues
	var line := MeshInstance3D.new()
	line.name = "VectorLine"
	var line_mesh = ClassDB.instantiate("CylinderMesh")
	if line_mesh == null:
		push_error("Failed to instantiate CylinderMesh using ClassDB")
		return # Avoid further errors
	line_mesh.top_radius = VECTOR_LINE_WIDTH / 2.0
	line_mesh.bottom_radius = VECTOR_LINE_WIDTH / 2.0
	line_mesh.height = vector_end_point.length() # Length of the vector
	line.mesh = line_mesh
	line.material_override = vector_material
	
	# Create a basis that aligns the cylinder with the vector direction
	var vector_dir = vector_end_point.normalized()
	var up = Vector3.UP
	if vector_dir.is_equal_approx(up) or vector_dir.is_equal_approx(-up):
		up = Vector3.RIGHT
	var x_axis = vector_dir.cross(up).normalized()
	var y_axis = vector_dir
	var z_axis = x_axis.cross(y_axis).normalized()
	var basis = Basis(x_axis, y_axis, z_axis)
	
	# Position and orient the cylinder
	line.transform = Transform3D(basis, vector_end_point / 2.0)
	parent_node.add_child(line)

	# Use ClassDB to instantiate ConeMesh for the arrowhead
	var arrowhead := MeshInstance3D.new()
	arrowhead.name = "VectorArrowhead"
	var arrowhead_mesh = ClassDB.instantiate("ConeMesh")
	if arrowhead_mesh == null:
		push_error("Failed to instantiate ConeMesh using ClassDB")
		return # Avoid further errors
	arrowhead_mesh.radius = ARROWHEAD_RADIUS
	arrowhead_mesh.height = ARROWHEAD_HEIGHT
	arrowhead.mesh = arrowhead_mesh
	arrowhead.material_override = vector_material

	# --- Alternative Arrowhead Orientation using look_at ---
	# Position the arrowhead origin at the endpoint
	arrowhead.global_position = parent_node.to_global(vector_end_point) 
	
	# Make it look slightly further along the vector direction from its position
	# Use parent's global transform to ensure correct world direction
	var look_target = arrowhead.global_position + parent_node.global_transform.basis * vector_dir
	arrowhead.look_at(look_target, Vector3.UP)
	
	# look_at points the mesh's -Z axis. Cone points along +Y. Rotate to align.
	arrowhead.rotate_object_local(Vector3.RIGHT, -PI / 2.0) 
	# --- End Alternative Orientation ---

	parent_node.add_child(arrowhead)
