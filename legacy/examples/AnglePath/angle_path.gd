# angle_path_scene.gd
extends Node2D

# --- Configuration ---
# Colors
const PATH_COLOR := Color(0.8, 0.7, 1.0, 0.5)
const DOT_COLOR := Color.WHITE
const ORANGE_COLOR := Color.ORANGE
const GREEN_COLOR := Color.GREEN
const BLUE_COLOR := Color.DODGER_BLUE
const LABEL_COLOR := Color.WHITE

# Sizes
const ANGLE_VISUAL_SIZE := 160.0
const ARC_RADIUS := ANGLE_VISUAL_SIZE / 2.5
const DOT_RADIUS := 8.0
const PATH_LINE_WIDTH := 1.5
const ANGLE_LINE_WIDTH := 3.0
const ARC_WIDTH := 3.0
const LABEL_FONT_SIZE := 24

# Dynamic Angle Settings
const MIN_ANGLE_DEG := 10.0
const MAX_ANGLE_DEG := 120.0
const ANGLE_CYCLE_SPEED := 2.0

# Animation settings
const ANIMATION_DURATION := 15.0
const PATH_SEGMENTS := 300

# Scale and Offset
const SCALE_FACTOR := 100.0
var screen_center := Vector2.ZERO

# --- UI Constants ---
const UI_MARGIN := 20.0
const UI_CONTROL_HEIGHT := 30.0
const UI_BUTTON_WIDTH := 80.0
const UI_SLIDER_H_OFFSET := UI_MARGIN + UI_BUTTON_WIDTH + 10.0

# --- State ---
var time_elapsed := 0.0
var path_points: PackedVector2Array = []
var current_position := Vector2.ZERO
var current_theta_degrees: float = MIN_ANGLE_DEG
var is_playing: bool = true # Start playing by default
var is_slider_dragging: bool = false # To prevent conflicts

# --- Node References ---
var angle_label: Label = null
var play_pause_button: Button = null
var time_slider: HSlider = null


func _ready() -> void:
	screen_center = get_viewport_rect().size / 2.0
	generate_path_points()

	# --- CREATE LABEL ---
	angle_label = Label.new()
	angle_label.add_theme_color_override("font_color", LABEL_COLOR)
	angle_label.add_theme_font_size_override("font_size", LABEL_FONT_SIZE)
	var sys_font = SystemFont.new()
	angle_label.add_theme_font_override("font", sys_font)
	add_child(angle_label)

	# --- CREATE PLAY/PAUSE BUTTON ---
	play_pause_button = Button.new()
	play_pause_button.text = "Pause" # Initial state is playing
	play_pause_button.custom_minimum_size = Vector2(UI_BUTTON_WIDTH, UI_CONTROL_HEIGHT)
	# Position bottom-left
	play_pause_button.position = Vector2(UI_MARGIN, get_viewport_rect().size.y - UI_CONTROL_HEIGHT - UI_MARGIN)
	# Connect signal
	play_pause_button.connect("pressed", _on_play_pause_pressed)
	add_child(play_pause_button)

	# --- CREATE TIME SLIDER ---
	time_slider = HSlider.new()
	time_slider.min_value = 0.0
	time_slider.max_value = ANIMATION_DURATION
	time_slider.step = 0.01 # Allow fine control
	time_slider.value = 0.0 # Initial value
	# Position next to button, fill width
	time_slider.position = Vector2(UI_SLIDER_H_OFFSET, play_pause_button.position.y)
	time_slider.size.x = get_viewport_rect().size.x - UI_SLIDER_H_OFFSET - UI_MARGIN
	# Try setting min height (actual height depends on theme)
	time_slider.custom_minimum_size.y = UI_CONTROL_HEIGHT
	# Connect signals
	time_slider.connect("value_changed", _on_slider_value_changed)
	# Also track dragging state to avoid fighting between _process and user input
	time_slider.connect("drag_started", func(): is_slider_dragging = true)
	time_slider.connect("drag_ended", func(_value_is_final): is_slider_dragging = false)
	add_child(time_slider)

	# Calculate initial state AFTER UI is created
	update_state(0.0)
	update_label_and_redraw() # Update label and draw initial frame

func _process(delta: float) -> void:
	# 1. Handle Time Progression if Playing
	if is_playing:
		time_elapsed += delta
		# Check for end of animation
		if time_elapsed >= ANIMATION_DURATION:
			time_elapsed = ANIMATION_DURATION
			is_playing = false # Stop playing
			play_pause_button.text = "Play" # Update button text
			print("Animation finished.")
			# Optionally loop:
			# time_elapsed = fmod(time_elapsed, ANIMATION_DURATION)

		# Update slider position smoothly ONLY if user isn't dragging it
		if time_slider and not is_slider_dragging:
			time_slider.set_value_no_signal(time_elapsed)

	# 2. Update State based on current time_elapsed (always happens, even if paused)
	var t = 0.0
	# Prevent division by zero if duration is zero
	if ANIMATION_DURATION > 0.0:
		# Clamp t to avoid issues slightly beyond duration boundary
		t = clampf(time_elapsed / ANIMATION_DURATION, 0.0, 1.0) * TAU
	else:
		t = 0.0

	update_state(t) # Update position and angle

	# 3. Update Visuals (Label and Drawing)
	update_label_and_redraw()


# --- Update Label Text/Position and Request Redraw ---
func update_label_and_redraw():
	# Update label text
	if angle_label:
		angle_label.text = "θ = %d°" % int(round(current_theta_degrees))
		angle_label.global_position = current_position + Vector2(DOT_RADIUS + ANGLE_VISUAL_SIZE + 15, -angle_label.size.y / 2)
		angle_label.visible = true

	# Request redraw for the main node
	queue_redraw()

# --- Signal Handlers ---
func _on_play_pause_pressed():
	is_playing = not is_playing # Toggle state
	if is_playing:
		play_pause_button.text = "Pause"
		# If user paused exactly at the end, reset to beginning to play again
		if time_elapsed >= ANIMATION_DURATION:
			time_elapsed = 0.0
	else:
		play_pause_button.text = "Play"

func _on_slider_value_changed(new_value: float):
	# Only update time if the user is actually dragging
	# Or if the value change wasn't triggered by set_value_no_signal
	# The is_slider_dragging flag helps manage this
	if is_slider_dragging:
		time_elapsed = new_value
		# When scrubbing, ensure playback state doesn't change unexpectedly
		# If user scrubs past end while playing was true, we should pause
		if time_elapsed >= ANIMATION_DURATION:
			is_playing = false
			play_pause_button.text = "Play"
		# Force immediate visual update based on new time
		var t = 0.0
		if ANIMATION_DURATION > 0.0:
			t = clampf(time_elapsed / ANIMATION_DURATION, 0.0, 1.0) * TAU
		update_state(t)
		update_label_and_redraw()

# --- Path Calculation ---
func parametric_function(t: float) -> Vector2:
	var x = 3.0 * sin(t * 2.0)
	var y = 2.0 * cos(t * 3.0)
	return Vector2(x, y) * SCALE_FACTOR + screen_center

# --- Path Point Generation ---
func generate_path_points() -> void:
	path_points.clear()
	for i in range(PATH_SEGMENTS + 1):
		var t = float(i) / PATH_SEGMENTS * TAU
		path_points.append(parametric_function(t))

# --- Update Moving Element State ---
func update_state(t: float) -> void:
	current_position = parametric_function(t)
	var angle_range = MAX_ANGLE_DEG - MIN_ANGLE_DEG
	var normalized_sin = (sin(t * ANGLE_CYCLE_SPEED) + 1.0) / 2.0
	current_theta_degrees = MIN_ANGLE_DEG + normalized_sin * angle_range

# --- Drawing ---
func _draw() -> void:
	if path_points.size() > 1:
		draw_polyline(path_points, PATH_COLOR, PATH_LINE_WIDTH, true)

	var theta_radians = deg_to_rad(current_theta_degrees)
	var green_end = current_position + Vector2(ANGLE_VISUAL_SIZE, 0)
	var orange_end = current_position + Vector2(ANGLE_VISUAL_SIZE, 0).rotated(theta_radians)

	draw_line(current_position, green_end, GREEN_COLOR, ANGLE_LINE_WIDTH, true)
	draw_line(current_position, orange_end, ORANGE_COLOR, ANGLE_LINE_WIDTH, true)

	draw_arc(
		current_position, ARC_RADIUS, 0.0, theta_radians, 64, BLUE_COLOR, ARC_WIDTH, true
	)
	draw_circle(current_position, DOT_RADIUS, DOT_COLOR)
