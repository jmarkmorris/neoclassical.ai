## Represents the entire visual assembly of the clock, including face, ticks, and hands.
## Handles the creation of static elements and the dynamic updating of hands based on time.
class_name ClockAssembly
extends Node3D

# --- Constants ---
## Standard colors used for clock elements.
const WHITE: Color = Color.WHITE
const BLUE: Color = Color.BLUE
const GREEN: Color = Color.GREEN
const RED: Color = Color.RED
## Yellow with alpha for path visualization (defined here for potential reuse).
const YELLOW_A: Color = Color(1.0, 1.0, 0.0, 0.7)

# --- Clock Geometry Constants ---
const HOUR_HAND_LENGTH_FACTOR: float = 0.5
const MINUTE_HAND_LENGTH_FACTOR: float = 0.7
const SECOND_HAND_LENGTH_FACTOR: float = 0.8
const MINUTE_TICK_LENGTH_FACTOR: float = 0.95
const HOUR_TICK_LENGTH_FACTOR: float = 0.85
const CENTER_DOT_RADIUS: float = 0.05
const FACE_CIRCLE_SEGMENTS: int = 64 # Used for TorusMesh sections/rings
const MINUTE_TICKS_COUNT: int = 60
const HOUR_TICKS_COUNT: int = 12

# --- Thickness Constants ---
const FACE_THICKNESS: float = 0.036 # Reduced by 10% from 0.04
const HOUR_TICK_THICKNESS: float = 0.03
const MINUTE_TICK_THICKNESS: float = 0.02
const HAND_THICKNESS: float = 0.03

# --- Properties ---
## The radius of the clock face circle. Determines the overall size.
var radius: float = 2.0

# References to Node3D nodes for dynamic parts (hands)
## Node3D pivot for the hour hand.
var hour_hand: Node3D
## Node3D pivot for the minute hand.
var minute_hand: Node3D
## Node3D pivot for the second hand.
var second_hand: Node3D
## MeshInstance3D for the small dot at the center of the clock.
var center_dot: MeshInstance3D

# References to static parts (face, ticks)
## MeshInstance3D for the clock face outline circle.
var face_circle: MeshInstance3D

# --- State ---
## Controls whether the clock hands update their rotation in _process.
var is_active: bool = true

# --- Initialization ---
## Constructor for the ClockAssembly.
## @param p_radius: The desired radius for the clock face.
func _init(p_radius: float = 2.0) -> void:
	radius = p_radius

## Called when the node enters the scene tree for the first time.
## Creates the visual elements of the clock.
func _ready() -> void:
	_create_static_elements()
	_create_dynamic_elements()
	_set_initial_hand_positions() # Set initial hand positions based on current time

# --- Private Methods ---
## Creates the static elements of the clock (face, ticks).
func _create_static_elements() -> void:
	# Create a standard material for static elements
	var static_material = StandardMaterial3D.new()
	static_material.albedo_color = WHITE
	static_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED # No lighting needed

	# 1. Face Circle (using TorusMesh for thickness)
	face_circle = MeshInstance3D.new()
	face_circle.name = "FaceCircle"
	var face_mesh = TorusMesh.new()
	# Calculate inner/outer radii based on desired center radius and thickness
	face_mesh.inner_radius = radius - FACE_THICKNESS / 2.0
	face_mesh.outer_radius = radius + FACE_THICKNESS / 2.0
	face_mesh.rings = 128 # Increased smoothness of the thickness profile significantly
	face_mesh.ring_segments = FACE_CIRCLE_SEGMENTS # Smoothness around the circle
	face_circle.mesh = face_mesh
	face_circle.material_override = static_material
	# Rotate the torus mesh instance 90 degrees around the X-axis to align with the XY plane
	face_circle.rotate_x(PI / 2.0)
	add_child(face_circle)

	# 2. Minute Ticks
	# Create individual cylinder meshes for minute ticks
	_create_thick_ticks(radius, MINUTE_TICKS_COUNT, MINUTE_TICK_LENGTH_FACTOR, MINUTE_TICK_THICKNESS, static_material, "MinuteTick")

	# 3. Hour Ticks
	# Create individual cylinder meshes for hour ticks
	_create_thick_ticks(radius, HOUR_TICKS_COUNT, HOUR_TICK_LENGTH_FACTOR, HOUR_TICK_THICKNESS, static_material, "HourTick")


## Helper function to create tick marks using CylinderMesh.
## @param p_radius: The base radius from which ticks extend inwards.
## @param count: The number of ticks to create.
## @param length_factor: Factor determining the inner end point (relative to radius).
## @param thickness: The diameter of the cylinder used for the tick.
## @param material: The material to apply to the ticks.
## @param name_prefix: String prefix for the tick node names.
func _create_thick_ticks(p_radius: float, count: int, length_factor: float, thickness: float, material: Material, name_prefix: String) -> void:
	var tick_length: float = p_radius * (1.0 - length_factor)
	var cylinder_radius: float = thickness / 2.0

	for i in range(count):
		# Calculate angle starting from 12 o'clock (positive Y = PI/2) and moving clockwise.
		var angle: float = PI / 2.0 - float(i) / count * TAU
		var direction: Vector3 = Vector3(cos(angle), sin(angle), 0)
		var outer_point: Vector3 = direction * p_radius
		var inner_point: Vector3 = outer_point * length_factor
		var midpoint: Vector3 = (outer_point + inner_point) / 2.0

		var tick_mesh_instance = MeshInstance3D.new()
		tick_mesh_instance.name = "%s_%d" % [name_prefix, i]

		var cylinder_mesh = CylinderMesh.new()
		cylinder_mesh.height = tick_length
		cylinder_mesh.top_radius = cylinder_radius
		cylinder_mesh.bottom_radius = cylinder_radius

		tick_mesh_instance.mesh = cylinder_mesh
		tick_mesh_instance.material_override = material

		# Position the cylinder at the midpoint of the tick line
		tick_mesh_instance.position = midpoint
		# Rotate the cylinder to align with the tick direction
		# Cylinder height is along its local Y axis. To align local Y with the calculated `angle`,
		# we need to rotate it by `angle - PI/2.0` (since local Y starts at PI/2).
		tick_mesh_instance.rotation.z = angle - PI / 2.0

		add_child(tick_mesh_instance)



## Creates the dynamic elements of the clock (hands, center dot).
func _create_dynamic_elements() -> void:
	# 1. Hour Hand
	hour_hand = _create_hand_pivot("HourHand", radius * HOUR_HAND_LENGTH_FACTOR, HAND_THICKNESS, BLUE)
	hour_hand.name = "HourHand"
	add_child(hour_hand)

	# 2. Minute Hand
	minute_hand = _create_hand_pivot("MinuteHand", radius * MINUTE_HAND_LENGTH_FACTOR, HAND_THICKNESS, GREEN)
	minute_hand.name = "MinuteHand"
	add_child(minute_hand)

	# 3. Second Hand
	second_hand = _create_hand_pivot("SecondHand", radius * SECOND_HAND_LENGTH_FACTOR, HAND_THICKNESS, RED)
	second_hand.name = "SecondHand"
	add_child(second_hand)

	# 4. Center Dot (Added last to render on top initially)
	center_dot = MeshInstance3D.new()
	center_dot.name = "CenterDot"
	var dot_mesh = SphereMesh.new()
	# Use slightly larger radius for dot mesh to ensure it covers hand bases
	dot_mesh.radius = CENTER_DOT_RADIUS
	dot_mesh.height = CENTER_DOT_RADIUS * 2.0 # Default height is 2*radius
	center_dot.mesh = dot_mesh
	var dot_material = StandardMaterial3D.new()
	dot_material.albedo_color = WHITE
	dot_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	# Higher render priority to ensure it's always on top of hands/ticks
	dot_material.render_priority = 1
	center_dot.material_override = dot_material
	add_child(center_dot)


## Helper function to create a pivot Node3D containing a thick hand mesh (Cylinder).
## @param name_prefix: String prefix for node names.
## @param length: The length of the hand.
## @param thickness: The diameter of the hand cylinder.
## @param color: The color of the hand.
## @return: A Node3D pivot containing the hand's MeshInstance3D.
func _create_hand_pivot(name_prefix: String, length: float, thickness: float, color: Color) -> Node3D:
	var pivot = Node3D.new()
	pivot.name = name_prefix + "Pivot" # Renamed pivot for clarity

	var hand_mesh_instance = MeshInstance3D.new()
	hand_mesh_instance.name = name_prefix + "Mesh"

	var cylinder_mesh = CylinderMesh.new()
	cylinder_mesh.height = length
	cylinder_mesh.top_radius = thickness / 2.0
	cylinder_mesh.bottom_radius = thickness / 2.0
	hand_mesh_instance.mesh = cylinder_mesh

	var material = StandardMaterial3D.new()
	material.albedo_color = color
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hand_mesh_instance.material_override = material

	# Offset the mesh instance so the base of the cylinder is at the pivot point (origin of Node3D)
	hand_mesh_instance.position.y = length / 2.0

	pivot.add_child(hand_mesh_instance)
	return pivot


## Sets the initial rotation of the clock hands based on the current system time.
## Called once from _ready().
func _set_initial_hand_positions() -> void:
	# Ensure hands have been created before trying to set them
	if not is_instance_valid(hour_hand) or \
	   not is_instance_valid(minute_hand) or \
	   not is_instance_valid(second_hand):
		printerr("Hands not ready for initial positioning.")
		return
	
	# 1. Get current time
	var now: Dictionary = Time.get_datetime_dict_from_system()
	var hour: float = now["hour"]
	var minute: float = now["minute"]
	var second: float = now["second"] + float(Time.get_ticks_usec() % 1000000) / 1000000.0

	# 2. Calculate initial progress (without speed modifiers here)
	var initial_hour_progress: float = fmod(hour, 12.0) + minute / 60.0 + second / 3600.0
	var initial_minute_progress: float = minute + second / 60.0
	var initial_second_progress: float = second

	# 3. Convert initial progress to initial angles
	# Godot rotation: Z-axis, positive is counter-clockwise (CCW).
	# Hands start pointing UP (+Y, which is PI/2 or 90 degrees CCW from +X).
	# Clockwise movement means decreasing the angle from PI/2.
	# Angle = Initial Angle (PI/2) - Fraction of Circle * TAU
	hour_hand.rotation.z = PI / 2.0 - (fmod(initial_hour_progress, 12.0) / 12.0) * TAU
	minute_hand.rotation.z = PI / 2.0 - (fmod(initial_minute_progress, 60.0) / 60.0) * TAU
	second_hand.rotation.z = PI / 2.0 - (fmod(initial_second_progress, 60.0) / 60.0) * TAU


## Called every frame. Updates the clock hand rotations based on elapsed time and speed factors.
## @param _delta: Time elapsed since the previous frame.
func _process(_delta: float) -> void:
	# Only update hands if the clock is active (controlled by main scene)
	if not is_active:
		return
		
	# Ensure hands are valid before rotating
	if not is_instance_valid(hour_hand) or \
	   not is_instance_valid(minute_hand) or \
	   not is_instance_valid(second_hand):
		return

	# Normal speed: Hour=TAU/12h, Minute=TAU/60m, Second=TAU/60s
	# TAU / (12 * 3600 seconds) for hour hand normal speed
	# TAU / (60 * 60 seconds) for minute hand normal speed
	# TAU / 60 seconds for second hand normal speed

	var hour_angular_speed: float = (TAU / (12.0 * 3600.0)) * 0.5 # Apply 0.5x speed modifier
	var minute_angular_speed: float = (TAU / 3600.0) * 10.0      # Apply 10x speed modifier
	var second_angular_speed: float = (TAU / 60.0) * 2.0        # Apply 2x speed modifier

	# Calculate rotation change for this frame (speed * time)
	# Negative sign because clockwise rotation decreases the angle in Godot's Z-rotation
	var hour_delta_angle: float = -hour_angular_speed * _delta
	var minute_delta_angle: float = -minute_angular_speed * _delta
	var second_delta_angle: float = -second_angular_speed * _delta

	# Apply rotation change to each hand
	hour_hand.rotate_z(hour_delta_angle)
	minute_hand.rotate_z(minute_delta_angle)
	second_hand.rotate_z(second_delta_angle)
