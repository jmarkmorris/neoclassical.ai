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
const FACE_CIRCLE_SEGMENTS: int = 64
const MINUTE_TICKS_COUNT: int = 60
const HOUR_TICKS_COUNT: int = 12

# --- Properties ---
## The radius of the clock face circle. Determines the overall size.
var radius: float = 2.0

# References to MeshInstance3D nodes for dynamic parts (hands)
## MeshInstance3D representing the hour hand.
var hour_hand: MeshInstance3D
## MeshInstance3D representing the minute hand.
var minute_hand: MeshInstance3D
## MeshInstance3D representing the second hand.
var second_hand: MeshInstance3D
## MeshInstance3D for the small dot at the center of the clock.
var center_dot: MeshInstance3D

# References to static parts (face, ticks)
## MeshInstance3D for the clock face outline circle.
var face_circle: MeshInstance3D
## MeshInstance3D holding the ImmediateMesh for all minute ticks.
var minute_ticks_mesh: MeshInstance3D
## MeshInstance3D holding the ImmediateMesh for all hour ticks.
var hour_ticks_mesh: MeshInstance3D

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
	_update_hands() # Set initial hand positions based on current time

# --- Private Methods ---
## Creates the static elements of the clock (face, ticks).
func _create_static_elements() -> void:
	# Create a standard material for static elements
	var static_material = StandardMaterial3D.new()
	static_material.albedo_color = WHITE
	static_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED # No lighting needed

	# 1. Face Circle
	face_circle = MeshInstance3D.new()
	face_circle.name = "FaceCircle"
	face_circle.mesh = _create_circle_mesh(radius, FACE_CIRCLE_SEGMENTS)
	face_circle.material_override = static_material
	add_child(face_circle)

	# 2. Minute Ticks
	minute_ticks_mesh = MeshInstance3D.new()
	minute_ticks_mesh.name = "MinuteTicks"
	minute_ticks_mesh.mesh = _create_ticks_mesh(radius, MINUTE_TICKS_COUNT, MINUTE_TICK_LENGTH_FACTOR)
	minute_ticks_mesh.material_override = static_material
	add_child(minute_ticks_mesh)

	# 3. Hour Ticks
	hour_ticks_mesh = MeshInstance3D.new()
	hour_ticks_mesh.name = "HourTicks"
	# Note: Manim used thicker stroke for hour ticks. ImmediateMesh lines have no thickness.
	# If thickness is desired, CylinderMesh/BoxMesh per tick would be needed.
	# Sticking to ImmediateMesh as per plan for now.
	hour_ticks_mesh.mesh = _create_ticks_mesh(radius, HOUR_TICKS_COUNT, HOUR_TICK_LENGTH_FACTOR)
	hour_ticks_mesh.material_override = static_material
	add_child(hour_ticks_mesh)


## Helper function to create a circle outline using ImmediateMesh.
## @param p_radius: The radius of the circle.
## @param segments: The number of line segments to approximate the circle.
## @return: An ImmediateMesh resource representing the circle.
func _create_circle_mesh(p_radius: float, segments: int) -> ImmediateMesh:
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	for i in range(segments + 1): # +1 to close the loop
		var angle: float = float(i) / segments * TAU
		var point: Vector3 = Vector3(cos(angle), sin(angle), 0) * p_radius
		mesh.surface_add_vertex(point)
	mesh.surface_end()
	return mesh


## Helper function to create tick marks using ImmediateMesh.
## @param p_radius: The base radius from which ticks extend inwards.
## @param count: The number of ticks to create.
## @param length_factor: The factor determining the inner end point of the tick (relative to radius).
## @return: An ImmediateMesh resource representing the ticks.
func _create_ticks_mesh(p_radius: float, count: int, length_factor: float) -> ImmediateMesh:
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINES)
	for i in range(count):
		var angle: float = float(i) / count * TAU
		var start_point: Vector3 = Vector3(cos(angle), sin(angle), 0) * p_radius
		var end_point: Vector3 = start_point * length_factor
		mesh.surface_add_vertex(start_point)
		mesh.surface_add_vertex(end_point)
	mesh.surface_end()
	return mesh


## Creates the dynamic elements of the clock (hands, center dot).
func _create_dynamic_elements() -> void:
	# 1. Hour Hand
	hour_hand = MeshInstance3D.new()
	hour_hand.name = "HourHand"
	hour_hand.mesh = _create_hand_mesh(radius * HOUR_HAND_LENGTH_FACTOR)
	var hour_material = StandardMaterial3D.new()
	hour_material.albedo_color = BLUE
	hour_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hour_hand.material_override = hour_material
	add_child(hour_hand)

	# 2. Minute Hand
	minute_hand = MeshInstance3D.new()
	minute_hand.name = "MinuteHand"
	minute_hand.mesh = _create_hand_mesh(radius * MINUTE_HAND_LENGTH_FACTOR)
	var minute_material = StandardMaterial3D.new()
	minute_material.albedo_color = GREEN
	minute_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	minute_hand.material_override = minute_material
	add_child(minute_hand)

	# 3. Second Hand
	second_hand = MeshInstance3D.new()
	second_hand.name = "SecondHand"
	second_hand.mesh = _create_hand_mesh(radius * SECOND_HAND_LENGTH_FACTOR)
	var second_material = StandardMaterial3D.new()
	second_material.albedo_color = RED
	second_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	second_hand.material_override = second_material
	add_child(second_hand)

	# 4. Center Dot (Added last to render on top initially)
	center_dot = MeshInstance3D.new()
	center_dot.name = "CenterDot"
	var dot_mesh = SphereMesh.new()
	dot_mesh.radius = CENTER_DOT_RADIUS
	dot_mesh.height = CENTER_DOT_RADIUS * 2.0 # Default height is 2*radius
	center_dot.mesh = dot_mesh
	var dot_material = StandardMaterial3D.new()
	dot_material.albedo_color = WHITE
	dot_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	# Optional: Higher render priority to ensure it's always on top
	# dot_material.render_priority = 1
	center_dot.material_override = dot_material
	add_child(center_dot)


## Helper function to create a simple line mesh for a clock hand pointing UP.
## @param length: The length of the hand.
## @return: An ImmediateMesh resource representing the hand line.
func _create_hand_mesh(length: float) -> ImmediateMesh:
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINES)
	# Start at origin, end pointing UP along Y-axis
	mesh.surface_add_vertex(Vector3.ZERO)
	mesh.surface_add_vertex(Vector3(0, length, 0))
	mesh.surface_end()
	return mesh


## Updates the rotation of the clock hands based on the current system time.
func _update_hands() -> void:
	# Ensure hands have been created before trying to update them
	if not is_instance_valid(hour_hand) or \
	   not is_instance_valid(minute_hand) or \
	   not is_instance_valid(second_hand):
		return # Don't update if nodes aren't ready

	# 1. Get current time
	var now: Dictionary = Time.get_datetime_dict_from_system()
	var hour: float = now["hour"]
	var minute: float = now["minute"]
	var second: float = now["second"] + float(Time.get_ticks_usec() % 1000000) / 1000000.0 # Add microseconds for smoother seconds

	# 2. Calculate progress with speed modifiers
	# Hour hand at 0.5x speed
	var hour_progress: float = (fmod(hour, 12.0) + minute / 60.0 + second / 3600.0) * 0.5
	# Minute hand at 10x speed
	var minute_progress: float = (minute + second / 60.0) * 10.0
	# Second hand at 2x speed
	var second_progress: float = second * 2.0

	# 3. Convert progress to angles
	# Godot rotation: Z-axis, positive is counter-clockwise (CCW).
	# Hands start pointing UP (+Y, which is PI/2 or 90 degrees CCW from +X).
	# Clockwise movement means decreasing the angle from PI/2.
	# Angle = Initial Angle (PI/2) - Fraction of Circle * TAU
	var target_hour_angle: float = PI / 2.0 - (fmod(hour_progress, 12.0) / 12.0) * TAU
	var target_minute_angle: float = PI / 2.0 - (fmod(minute_progress, 60.0) / 60.0) * TAU
	var target_second_angle: float = PI / 2.0 - (fmod(second_progress, 60.0) / 60.0) * TAU

	# 4. Apply rotations
	# We set the absolute rotation around the Z axis each frame.
	hour_hand.rotation.z = target_hour_angle
	minute_hand.rotation.z = target_minute_angle
	second_hand.rotation.z = target_second_angle


## Called every frame. Updates the clock hands.
## @param _delta: Time elapsed since the previous frame (unused).
func _process(_delta: float) -> void:
	_update_hands()
