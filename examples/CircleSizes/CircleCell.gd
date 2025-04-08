extends Node3D

# Node references - will be assigned in _ready after ensuring nodes exist
var left_circle: MeshInstance3D
var right_circle: MeshInstance3D
var radius_label: Label3D

# Materials (Consider creating these as resources in the editor and exporting them)
var mat_blue: StandardMaterial3D
var mat_red: StandardMaterial3D

# Constants matching CircleSizes.gd
const PURE_BLUE = Color.BLUE
const PURE_RED = Color.RED
const WHITE = Color.WHITE

# Relative positions of elements within the cell (in world units)
const LEFT_CIRCLE_OFFSET = Vector3(0.25, -0.25, 0)
const RIGHT_CIRCLE_OFFSET = Vector3(0.75, -0.25, 0)
const LABEL_OFFSET = Vector3(0.5, -0.75, 0)

# Label configuration
const LABEL_FONT_SIZE = 0.15 # Adjusted size for better fit
const LABEL_PIXEL_SIZE = 0.001 # Controls render quality/sharpness


func _ready():
	# --- Ensure required nodes exist ---
	# LeftCircle
	left_circle = get_node_or_null("LeftCircle")
	if not left_circle:
		print("Creating LeftCircle programmatically.")
		left_circle = MeshInstance3D.new()
		left_circle.name = "LeftCircle"
		add_child(left_circle)

	# RightCircle
	right_circle = get_node_or_null("RightCircle")
	if not right_circle:
		print("Creating RightCircle programmatically.")
		right_circle = MeshInstance3D.new()
		right_circle.name = "RightCircle"
		add_child(right_circle)

	# RadiusLabel
	radius_label = get_node_or_null("RadiusLabel")
	if not radius_label:
		# print("Creating RadiusLabel programmatically.")
		radius_label = Label3D.new()
		radius_label.name = "RadiusLabel"
		add_child(radius_label)
	# --- End Node Creation ---


	# Create materials programmatically (alternative: export vars and assign in editor)
	mat_blue = StandardMaterial3D.new()
	mat_blue.albedo_color = PURE_BLUE
	mat_blue.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED

	mat_red = StandardMaterial3D.new()
	mat_red.albedo_color = PURE_RED
	mat_red.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED

	# Assign materials
	if left_circle:
		left_circle.material_override = mat_blue
	if right_circle:
		right_circle.material_override = mat_red

	# Configure Label3D
	if radius_label:
		radius_label.text = "r = 0.000" # Initial text
		radius_label.font_size = LABEL_FONT_SIZE
		radius_label.modulate = WHITE # Use modulate for color
		radius_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		radius_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		radius_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		radius_label.pixel_size = LABEL_PIXEL_SIZE
		# Explicitly load and set the default theme font
		var default_font = ThemeDB.get_fallback_font()
		if default_font:
			radius_label.font = default_font
		else:
			push_warning("Could not load default theme font for Label3D.")


# Called from CircleSizes.gd to configure this cell instance
func update_display(radius: float):
	# Ensure nodes are ready
	if not is_node_ready():
		await ready # Wait if called before _ready completes

	# Validate radius
	if radius <= 0:
		push_warning("Invalid radius provided: %f" % radius)
		# Optionally hide the elements or set a default small size
		if left_circle: left_circle.visible = false
		if right_circle: right_circle.visible = false
		if radius_label: radius_label.visible = false
		return
	else:
		if left_circle: left_circle.visible = true
		if right_circle: right_circle.visible = true
		if radius_label: radius_label.visible = true

	# Update Circles
	# Create new SphereMesh instances to ensure radius is updated correctly
	var sphere_mesh = SphereMesh.new()
	sphere_mesh.radius = radius
	# Height should be diameter for a sphere
	sphere_mesh.height = radius * 2.0
	# Increase detail for smoother spheres, especially small ones
	sphere_mesh.radial_segments = 16
	sphere_mesh.rings = 8

	if left_circle:
		left_circle.mesh = sphere_mesh
		left_circle.position = LEFT_CIRCLE_OFFSET

	# --- Enable RightCircle update ---
	if right_circle:
		# Need a separate mesh instance for the right circle
		var sphere_mesh_right = SphereMesh.new()
		sphere_mesh_right.radius = radius
		sphere_mesh_right.height = radius * 2.0
		sphere_mesh_right.radial_segments = 16
		sphere_mesh_right.rings = 8
		right_circle.mesh = sphere_mesh_right
		right_circle.position = RIGHT_CIRCLE_OFFSET
	# --- End RightCircle enable ---

	# Update Label
	if radius_label:
		radius_label.text = "r = %.3f" % radius
		radius_label.position = LABEL_OFFSET
