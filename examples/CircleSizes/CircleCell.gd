extends Node3D

# Node references (ensure these nodes exist in CircleCell.tscn)
@onready var left_circle: MeshInstance3D = $LeftCircle
@onready var right_circle: MeshInstance3D = $RightCircle
@onready var radius_label: Label3D = $RadiusLabel

# Materials (Consider creating these as resources in the editor and exporting them)
var mat_blue: StandardMaterial3D
var mat_red: StandardMaterial3D

# Constants matching CircleSizes.gd
const PURE_BLUE = Color.BLUE
const PURE_RED = Color.RED
const WHITE = Color.WHITE

# Relative positions based on Manim script (Step 6 Correction in convert.md)
const LEFT_CIRCLE_OFFSET = Vector3(0.25, -0.25, 0)
const RIGHT_CIRCLE_OFFSET = Vector3(0.75, -0.25, 0)
const LABEL_OFFSET = Vector3(0.5, -0.75, 0)

# Label configuration
const LABEL_FONT_SIZE = 0.1 # Adjust as needed (world units)
const LABEL_PIXEL_SIZE = 0.001 # Controls render quality/sharpness


func _ready():
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
		# Consider loading a font resource here:
		# radius_label.font = load("res://path/to/your/font.tres")


# Called from CircleSizes.gd to configure this cell instance
func update_display(manim_radius: float):
	# Ensure nodes are ready
	if not is_node_ready():
		await ready # Wait if called before _ready completes

	# Validate radius
	if manim_radius <= 0:
		push_warning("Invalid radius provided: %f" % manim_radius)
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
	sphere_mesh.radius = manim_radius
	# Height should be diameter for a sphere
	sphere_mesh.height = manim_radius * 2.0
	# Increase detail for smoother spheres, especially small ones
	sphere_mesh.radial_segments = 16
	sphere_mesh.rings = 8

	if left_circle:
		left_circle.mesh = sphere_mesh
		left_circle.position = LEFT_CIRCLE_OFFSET

	if right_circle:
		# Need a separate mesh instance for the right circle
		var sphere_mesh_right = SphereMesh.new()
		sphere_mesh_right.radius = manim_radius
		sphere_mesh_right.height = manim_radius * 2.0
		sphere_mesh_right.radial_segments = 16
		sphere_mesh_right.rings = 8
		right_circle.mesh = sphere_mesh_right
		right_circle.position = RIGHT_CIRCLE_OFFSET

	# Update Label
	if radius_label:
		radius_label.text = "r = %.3f" % manim_radius
		radius_label.position = LABEL_OFFSET
