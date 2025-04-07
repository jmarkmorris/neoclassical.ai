# angle_path_scene.gd
extends Node2D

# --- Configuration ---
const INDIGO_COLOR := Color("4B0082") # Just for reference, background set in project settings
const PATH_COLOR := Color.YELLOW * Color(1, 1, 1, 0.3) # Yellow with low opacity
const ANGLE_LINE_COLOR := Color.WHITE
const ANGLE_ARC_COLOR := Color.GREEN
const ANGLE_VISUAL_SIZE := 30.0 # Controls the length of the angle lines and arc radius
const ANGLE_OPENING := PI / 4.0 # The fixed angle opening (e.g., 45 degrees)
const PATH_LINE_WIDTH := 2.0
const ANGLE_LINE_WIDTH := 2.0
const ANGLE_ARC_WIDTH := 2.0

const ANIMATION_DURATION := 15.0
const PATH_SEGMENTS := 200 # Number of segments to draw the static path

# --- Scale and Offset ---
# Adjust these to fit the curve nicely in the viewport
const SCALE_FACTOR := 100.0
var screen_center := Vector2.ZERO # Will be set in _ready

# --- State ---
var time_elapsed := 0.0
var path_points: PackedVector2Array = [] # To store points for drawing the full path
var current_position := Vector2.ZERO
var current_rotation_angle := 0.0
var is_animating := true

# --- Preload or define the Angle representation if it were more complex ---
# For this case, we'll draw directly in the main node's _draw function.
# If the angle had its own logic/nodes, you might use:
# const AngleGroup = preload("res://angle_group.gd") # If you made a separate scene/script


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Calculate screen center (important for positioning)
	screen_center = get_viewport_rect().size / 2.0
	
	# Pre-calculate points for drawing the static background path
	generate_path_points()

	# Initial state calculation (optional, _process handles it)
	update_angle_state(0.0) # Calculate state at t=0
	
	# Force an initial draw
	queue_redraw()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if not is_animating:
		return

	time_elapsed += delta

	if time_elapsed >= ANIMATION_DURATION:
		time_elapsed = ANIMATION_DURATION # Clamp to end
		is_animating = false             # Stop animation
		print("Animation finished.")
		# You could add a delay here using a Timer if you want to wait after finishing
		# $Timer.start() 
		
	# Calculate current parameter 't' based on time elapsed
	# Manim's t_range is [0, TAU], so we map time_elapsed to this range
	var t = (time_elapsed / ANIMATION_DURATION) * TAU 
	
	# Ensure t doesn't go exactly to 0 if initial_alpha was meant to avoid it,
	# although the tangent calculation should handle t=0 okay.
	# Manim used initial_alpha = 0.001, potentially to avoid division by zero 
	# or degenerate cases in its specific AngleGroup init.
	# Here, we just map the time.
	
	update_angle_state(t)
	
	# Request a redraw to show the updated angle position/rotation
	queue_redraw()

# --- Path Calculation ---
func parametric_function(t: float) -> Vector2:
	# Same parametric function as in Manim, scaled and centered
	var x = 3.0 * sin(t * 2.0)
	var y = 2.0 * cos(t * 3.0) 
	# Manim's y is often inverted compared to Godot's screen coordinates
	# depending on setup, but let's keep it direct for now.
	# If it looks upside down, use: var y = -2.0 * cos(t * 3.0)
	return Vector2(x, y) * SCALE_FACTOR + screen_center

func path_tangent(t: float) -> Vector2:
	# Calculate the derivative (tangent vector) of the parametric function
	# dx/dt = 3 * cos(t * 2) * 2 = 6 * cos(2*t)
	# dy/dt = 2 * (-sin(t * 3)) * 3 = -6 * sin(3*t)
	var tx = 6.0 * cos(t * 2.0)
	var ty = -6.0 * sin(t * 3.0)
	
	var tangent = Vector2(tx, ty)
	
	# Avoid division by zero if tangent is zero length (at cusps/stops)
	if tangent.length_squared() > 0.0001:
		return tangent.normalized()
	else:
		# If tangent is zero, try slight offset or return previous tangent?
		# For simplicity, return horizontal direction. Or calculate based on t+epsilon
		var t_eps = t + 0.001 
		tx = 6.0 * cos(t_eps * 2.0)
		ty = -6.0 * sin(t_eps * 3.0)
		tangent = Vector2(tx, ty)
		if tangent.length_squared() > 0.0001:
			return tangent.normalized()
		else:
			return Vector2.RIGHT # Fallback direction

# --- State Update ---
func update_angle_state(t: float) -> void:
	current_position = parametric_function(t)
	var tangent_direction := path_tangent(t)
	# The rotation angle is the angle of the tangent vector
	current_rotation_angle = tangent_direction.angle() 

# --- Path Point Generation ---
func generate_path_points() -> void:
	path_points.clear()
	for i in range(PATH_SEGMENTS + 1):
		var t = float(i) / PATH_SEGMENTS * TAU
		path_points.append(parametric_function(t))

# --- Drawing ---
func _draw() -> void:
	# 1. Draw the full static path (subtly)
	if path_points.size() > 1:
		draw_polyline(path_points, PATH_COLOR, PATH_LINE_WIDTH, true) # Antialiased

	# 2. Draw the moving "AngleGroup" representation
	if is_animating or time_elapsed >= ANIMATION_DURATION: # Draw final frame too
		# Lines originate from current_position, rotated by current_rotation_angle
		# The angle lines themselves have a fixed opening (ANGLE_OPENING)
		
		# Calculate end points relative to the angle's orientation
		var half_angle = ANGLE_OPENING / 2.0
		
		# Point B (upper line)
		var p_b = current_position + Vector2(ANGLE_VISUAL_SIZE, 0).rotated(current_rotation_angle - half_angle)
		# Point C (lower line)
		var p_c = current_position + Vector2(ANGLE_VISUAL_SIZE, 0).rotated(current_rotation_angle + half_angle)

		# Draw line A->B (A is current_position)
		draw_line(current_position, p_b, ANGLE_LINE_COLOR, ANGLE_LINE_WIDTH, true)
		# Draw line A->C
		draw_line(current_position, p_c, ANGLE_LINE_COLOR, ANGLE_LINE_WIDTH, true)
		
		# Draw the arc
		# Note: draw_arc angles are relative to Vector2.RIGHT (positive x-axis)
		var start_arc_angle = current_rotation_angle - half_angle
		var end_arc_angle = current_rotation_angle + half_angle
		
		draw_arc(
			current_position,      # center
			ANGLE_VISUAL_SIZE / 2.0, # radius (make it smaller than lines)
			start_arc_angle,       # start_angle (radians)
			end_arc_angle,         # end_angle (radians)
			32,                    # point_count (smoothness)
			ANGLE_ARC_COLOR,       # color
			ANGLE_ARC_WIDTH,       # width
			true                   # antialiased
		)
