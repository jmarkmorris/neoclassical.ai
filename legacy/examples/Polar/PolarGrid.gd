@tool
extends Node3D

# Configuration constants based on design.md and reference image/script
const WHITE_COLOR := Color(1.0, 1.0, 1.0)
# const RED_ORANGE_COLOR := Color(1.0, 0.27, 0.0) # Removed - No longer used after vector removal
const RADII := [1.0, 2.0, 3.0, 4.0]
const MAX_RADIUS := 4.0
const NUM_RADIAL_LINES := 12
const LABEL_OFFSET := 0.3 # Base distance labels are placed outside the max radius
# Label3D font size - larger values increase detail but require smaller pixel_size
const LABEL_FONT_SIZE := 128 
# Label3D pixel size - smaller values make text appear larger and sharper for a given font_size
const LABEL_PIXEL_SIZE := 0.0020 

const CIRCLE_SEGMENTS := 128 # Number of segments for drawing circles (higher is smoother)

# --- Scene Layout Constants ---
const CAMERA_ORTHO_SIZE := 11.0 # Orthogonal camera view size
const CAMERA_Z_POS := 10.0      # Camera distance from XY plane
const GRID_Y_OFFSET := -0.5     # Vertical offset for the entire grid container
const TITLE_Y_OFFSET_FROM_MAX_RADIUS := 0.7 # Title distance above max radius circle
const RADIUS_LABEL_OFFSET_FACTOR := 1.0 # Multiplier for radius label distance below X-axis
const AZIMUTH_LABEL_OFFSET_FACTOR := 1.5 # Multiplier for azimuth label distance outside max radius

# Node references (optional, could also find_child)
var camera: Camera3D
var title_label: Label3D
var grid_container: Node3D

# Materials
var white_material: StandardMaterial3D

# --- Initialization & Scene Building ---

# Called when the node enters the scene tree for the first time.
# In @tool mode, this also runs in the editor.
func _ready():
	# Use call_deferred to ensure node manipulation happens safely,
	# especially important in @tool mode during editor initialization or script reloading.
	call_deferred("_clear_children_and_rebuild")

# Clears existing children and rebuilds the entire visualization scene.
# This function orchestrates the creation of all visual elements.
# Essential for @tool mode to reflect script changes without manual scene clearing.
func _clear_children_and_rebuild():
	# Clear previous children safely before rebuilding to prevent duplicates
	for child in get_children():
		child.queue_free()

	# --- Camera Setup ---
	# Create and configure the main camera for viewing the 2D visualization in 3D space.
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL # Use orthogonal for a flat 2D look
	# Set camera size using constant
	camera.size = CAMERA_ORTHO_SIZE 
	# Position camera along the Z-axis using constant
	camera.transform.origin = Vector3(0, 0, CAMERA_Z_POS) 
	camera.current = true # Make this the active camera for the scene
	add_child(camera)

	# --- Title Label Setup ---
	# Create and configure the main title label.
	# Pass a specific font size override to make it larger than grid labels.
	title_label = _create_label("Polar Coordinates Visualization", Vector3.ZERO, 256) 
	# Position title above the main grid area using constant
	title_label.transform.origin = Vector3(0, MAX_RADIUS + TITLE_Y_OFFSET_FROM_MAX_RADIUS, 0)
	add_child(title_label)

	# --- Grid Container Setup ---
	# Create a container Node3D to hold all grid elements (circles, lines, labels).
	# This allows positioning the entire grid group easily.
	grid_container = Node3D.new()
	grid_container.name = "GridContainer"
	# Position grid container using constant
	grid_container.position = Vector3(0, GRID_Y_OFFSET, 0)
	add_child(grid_container)
		
	# --- Material Initialization and Grid Element Creation ---
	# Initialize materials needed for the grid elements.
	_initialize_materials()
	# Call functions to create grid elements, passing the container node as parent.
	_create_circles(grid_container)
	_create_radial_lines(grid_container)
	_create_labels(grid_container)

# --- Material Initialization ---

# Creates and configures the materials used for the visualization elements.
func _initialize_materials():
	# Configure the white material used for grid lines and labels.
	white_material = StandardMaterial3D.new()
	white_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED # Ignore lighting
	white_material.albedo_color = WHITE_COLOR # Base color
	white_material.emission_enabled = true # Use emission for consistent brightness
	white_material.emission = WHITE_COLOR # Set emission color to match albedo

# Helper to convert polar coordinates to Cartesian Vector3 (on XY plane)
func _polar_to_cartesian(r: float, theta: float) -> Vector3:
	return Vector3(r * cos(theta), r * sin(theta), 0)

# --- Grid Element Creation Functions ---

# Creates the concentric circle grid lines using ImmediateMesh.
func _create_circles(parent_node: Node3D):
	for r: float in RADII: # Iterate through the defined radii (e.g., 1.0, 2.0, ...)
		# Create ImmediateMesh and a MeshInstance to render it for each circle
		var immediate_mesh: ImmediateMesh = ImmediateMesh.new()
		var mesh_instance: MeshInstance3D = MeshInstance3D.new()
		mesh_instance.name = "Circle_r" + str(r)
		mesh_instance.mesh = immediate_mesh
		mesh_instance.material_override = white_material
		parent_node.add_child(mesh_instance)

		# Begin defining the line strip for the circle
		immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
		# Add vertices around the circle
		for i: int in range(CIRCLE_SEGMENTS + 1): # +1 to close the loop
			var angle: float = float(i) / CIRCLE_SEGMENTS * TAU # TAU is 2*PI
			immediate_mesh.surface_add_vertex(_polar_to_cartesian(r, angle))
		immediate_mesh.surface_end() # Finish defining the surface

# Creates the radial grid lines extending from the origin using ImmediateMesh.
func _create_radial_lines(parent_node: Node3D):
	for i: int in range(NUM_RADIAL_LINES): # Iterate for each required line (e.g., 12 lines)
		var angle: float = float(i) / NUM_RADIAL_LINES * TAU # Calculate angle for this line
		var end_point: Vector3 = _polar_to_cartesian(MAX_RADIUS, angle) # Calculate endpoint at max radius
		
		# Create ImmediateMesh and MeshInstance for each radial line
		var immediate_mesh: ImmediateMesh = ImmediateMesh.new()
		var mesh_instance: MeshInstance3D = MeshInstance3D.new()
		mesh_instance.name = "RadialLine_" + str(i)
		mesh_instance.mesh = immediate_mesh
		mesh_instance.material_override = white_material
		parent_node.add_child(mesh_instance)

		# Begin defining the line segment
		immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
		immediate_mesh.surface_add_vertex(Vector3.ZERO) # Line starts at origin
		immediate_mesh.surface_add_vertex(end_point)   # Line ends at max radius
		immediate_mesh.surface_end() # Finish defining the surface

# Creates the Label3D nodes for radius values and azimuth angle markers.
func _create_labels(parent_node: Node3D):
	# --- Radius Labels --- (Placed along the positive X-axis)
	for r: float in RADII:
		# Position label slightly below the corresponding radius point on the X-axis using constant factor
		var label_pos: Vector3 = Vector3(r, -LABEL_OFFSET * RADIUS_LABEL_OFFSET_FACTOR, 0) 
		var label_text: String = str(snapped(r, 0.1)) # Format radius value (e.g., "1.0")
		var radius_label: Label3D = _create_label(label_text, label_pos) # Use helper to create label
		radius_label.name = "RadiusLabel_" + str(r)
		parent_node.add_child(radius_label)

	# --- Azimuth Labels --- (Placed around the perimeter)
	# Define the text representation for each angle label
	var azimuth_texts: PackedStringArray = ["0", "π/6", "π/3", "π/2", "2π/3", "5π/6", "π", "7π/6", "4π/3", "3π/2", "5π/3", "11π/6"]
	for i: int in range(NUM_RADIAL_LINES):
		var angle: float = float(i) / NUM_RADIAL_LINES * TAU # Calculate angle for this label
		# Position label slightly further outside the max radius circle using constant factor
		var label_pos: Vector3 = _polar_to_cartesian(MAX_RADIUS + LABEL_OFFSET * AZIMUTH_LABEL_OFFSET_FACTOR, angle) 
		var azimuth_label: Label3D = _create_label(azimuth_texts[i], label_pos) # Use helper
		azimuth_label.name = "AzimuthLabel_" + str(i)
		parent_node.add_child(azimuth_label)

# --- Label Creation Helper ---

# Creates and configures a Label3D node with common settings used throughout the scene.
# Allows overriding the default font size for specific labels (like the title).
# Note: Positioning is set based on the 'position' argument passed by the caller.
func _create_label(text: String, position: Vector3, font_size_override: int = -1) -> Label3D:
	var label: Label3D = Label3D.new()
	label.text = text
	# Use font size override if provided (>0), otherwise use the default constant
	label.font_size = font_size_override if font_size_override > 0 else LABEL_FONT_SIZE
	label.pixel_size = LABEL_PIXEL_SIZE # Controls sharpness/apparent size
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED # Ensure label always faces camera
	label.no_depth_test = true # Render label on top of other geometry
	label.modulate = WHITE_COLOR # Set label color
	label.transform.origin = position # Set initial position based on argument
	# Center align text horizontally and vertically within the label's boundary
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return label
