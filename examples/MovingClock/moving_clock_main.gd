## Main script for the Clock example scene.
## Sets up the environment, creates the clock path, instantiates the clock assembly,
## and manages the animation along the path.
extends Node3D

# Preload the ClockAssembly script. This allows Godot to recognize the type.
const ClockAssembly: Script = preload("res://clock_assembly.gd")

# --- Constants ---
const CAMERA_Z_POSITION: float = 10.0
const PATH_PARAM_X_AMP: float = 3.0
const PATH_PARAM_X_FREQ: float = 2.0
const PATH_PARAM_Y_AMP: float = 2.0
const PATH_PARAM_Y_FREQ: float = 3.0
const PATH_SAMPLE_STEPS: int = 300 # Increased for smoother path
const ORTHOGONAL_CAMERA_SIZE: float = 5.0 # Controls the vertical view size
const PATH_ANIMATION_DURATION: float = 15.0
const PATH_THICKNESS: float = 0.05 # Radius for the TubeTrailMesh
const INITIAL_CLOCK_RADIUS_FACTOR: float = 2.0 * 0.95 * 0.95 # Matches Manim example
const GLOBAL_SCALE: float = 0.6 # Scale factor for 40% reduction

# --- UI Constants ---
const UI_MARGIN := 20.0
const UI_CONTROL_HEIGHT := 30.0
const UI_BUTTON_WIDTH := 80.0
const UI_BUTTON_FONT_SIZE := 48 # Increased font size for the button
const UI_SLIDER_H_OFFSET := UI_MARGIN + UI_BUTTON_WIDTH + 10.0

# --- State Variables ---
var time_elapsed := 0.0
var is_playing: bool = true # Start playing by default
var is_slider_dragging: bool = false # To prevent conflicts

# --- Properties ---
## Instance of the clock assembly node.
var clock_assembly_instance: ClockAssembly
## The Path3D node defining the clock's movement trajectory.
var path_node: Path3D
## The PathFollow3D node that moves the clock along the path.
var path_follow_node: PathFollow3D
## Optional MeshInstance3D to visualize the path itself.
var path_visualization_mesh: MeshInstance3D
## UI Elements (added to CanvasLayer)
var play_pause_button: Button = null
var time_slider: HSlider = null
## CanvasLayer for UI
var ui_layer: CanvasLayer = null

## Called when the node enters the scene tree for the first time.
## Orchestrates the setup of the entire scene.
func _ready() -> void:
	print("Clock main scene ready.")
	_setup_environment()
	_create_path()
	_create_clock()
	_setup_path_following()
	_setup_ui() # Setup UI elements
	# Animation is now driven by _process

## Sets up the basic 3D environment, including lighting and camera.
func _setup_environment() -> void:
	# Background color is set in project.godot (Indigo)

	# Add a simple directional light
	var light = DirectionalLight3D.new()
	light.light_energy = 1.0
	light.shadow_enabled = true # Enable shadows if needed later
	# Rotate the light for better illumination angle
	light.rotation_degrees = Vector3(-45, -45, 0)
	add_child(light)
	print("Added DirectionalLight3D.")

	# Add a camera to view the scene
	var camera = Camera3D.new()
	# Position the camera back along the Z-axis to see the origin
	camera.position = Vector3(0, 0, CAMERA_Z_POSITION)
	# Point the camera towards the origin
	camera.look_at(Vector3.ZERO)
	# Use Orthogonal projection for a flat 2D look
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = ORTHOGONAL_CAMERA_SIZE # Set the view size
	add_child(camera)
	print("Added Camera3D.")

## Creates the parametric path for the clock to follow.
func _create_path() -> void:
	print("Creating parametric path...")
	# 1. Create Path3D node
	path_node = Path3D.new()
	path_node.name = "ClockPath"
	add_child(path_node)

	# 2. Create Curve3D resource
	var curve = Curve3D.new()

	# 3. Define the parametric function (same as Manim example)
	# Using a Lambda function here for conciseness
	var path_func = func(t: float) -> Vector3:
		return Vector3(
			PATH_PARAM_X_AMP * sin(t * PATH_PARAM_X_FREQ) * GLOBAL_SCALE, # Apply scale
			PATH_PARAM_Y_AMP * cos(t * PATH_PARAM_Y_FREQ) * GLOBAL_SCALE, # Apply scale
			0.0 # Keep it in the XY plane
		)

	# 4. Sample points along the curve
	for i in range(PATH_SAMPLE_STEPS + 1):
		var t: float = float(i) / PATH_SAMPLE_STEPS * TAU # t from 0 to TAU
		var point: Vector3 = path_func.call(t)
		curve.add_point(point) # Add the calculated point to the curve

	# 5. Assign the curve to the Path3D node
	path_node.curve = curve
	print("Path3D node created with %d points." % curve.get_point_count())

	# 6. (Optional) Visualize the path
	path_visualization_mesh = MeshInstance3D.new()
	path_visualization_mesh.name = "PathVisualization"

	# Use ImmediateMesh for path visualization (more robust than TubeTrailMesh here)
	var path_mesh = ImmediateMesh.new()

	var path_material = StandardMaterial3D.new()
	# Use a muted, semi-transparent grey color
	path_material.albedo_color = Color(0.6, 0.6, 0.6, 0.5)
	path_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	path_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	path_visualization_mesh.mesh = path_mesh
	path_visualization_mesh.material_override = path_material

	# Draw the lines using the curve points
	path_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	for point in curve.get_baked_points(): # Use baked points for ImmediateMesh
		path_mesh.surface_add_vertex(point)
	path_mesh.surface_end()

	add_child(path_visualization_mesh) # Add visualization directly to the main scene
	print("Added path visualization mesh.")


## Instantiates the ClockAssembly node.
func _create_clock() -> void:
	print("Instantiating ClockAssembly...")
	# Instantiate the ClockAssembly using its class_name
	# Pass the adjusted radius factor defined as a constant
	clock_assembly_instance = ClockAssembly.new(INITIAL_CLOCK_RADIUS_FACTOR)
	clock_assembly_instance.name = "ClockAssemblyInstance"
	# Apply the global scale reduction to the clock instance itself
	clock_assembly_instance.scale = Vector3(GLOBAL_SCALE, GLOBAL_SCALE, GLOBAL_SCALE)

	# IMPORTANT: Do NOT add clock_assembly_instance as a child of the main scene here.
	# It will be added as a child of the PathFollow3D node in the next step.
	print("ClockAssembly instance created with radius: %f" % INITIAL_CLOCK_RADIUS_FACTOR)


## Sets up the PathFollow3D node to link the clock to the path.
func _setup_path_following() -> void:
	# Ensure the path and clock instance exist before proceeding
	if not is_instance_valid(path_node) or not is_instance_valid(clock_assembly_instance):
		printerr("Path node or clock instance is not valid for path following setup.")
		return

	print("Setting up PathFollow3D...")
	# 1. Create PathFollow3D node
	path_follow_node = PathFollow3D.new()
	path_follow_node.name = "ClockPathFollower"

	# 2. Configure PathFollow3D properties
	# ROTATION_NONE prevents the follower from rotating its children.
	path_follow_node.rotation_mode = PathFollow3D.ROTATION_NONE
	path_follow_node.loop = true # Make the movement loop continuously

	# 3. Parent the clock assembly to the PathFollow3D node
	# This makes the clock assembly move and rotate with the follower
	path_follow_node.add_child(clock_assembly_instance)
	print("Added ClockAssemblyInstance as child of PathFollow3D.")

	# 4. Parent the PathFollow3D node to the Path3D node
	# This connects the follower to the path it should follow
	path_node.add_child(path_follow_node)
	print("Added PathFollow3D as child of Path3D.")


## Sets up the UI elements (Button, Slider) on a CanvasLayer.
func _setup_ui() -> void:
	# Create a CanvasLayer to hold UI elements
	ui_layer = CanvasLayer.new()
	ui_layer.name = "UILayer"
	add_child(ui_layer)

	# --- CREATE CONTAINER ---
	var bottom_hbox = HBoxContainer.new()
	bottom_hbox.name = "BottomControlsContainer"
	# Anchor to bottom, stretch horizontally
	bottom_hbox.anchor_left = 0.0
	bottom_hbox.anchor_top = 1.0
	bottom_hbox.anchor_right = 1.0
	bottom_hbox.anchor_bottom = 1.0
	# Set margins relative to anchors (negative top margin to pull it up from bottom)
	bottom_hbox.offset_left = UI_MARGIN * 2.0 # Add more horizontal margin too
	bottom_hbox.offset_top = -(UI_CONTROL_HEIGHT + UI_MARGIN * 2.0) # Move further up
	bottom_hbox.offset_right = -UI_MARGIN * 2.0 # Add more horizontal margin too
	bottom_hbox.offset_bottom = -UI_MARGIN * 2.0 # Move further up
	# Add some spacing between button and slider
	bottom_hbox.add_theme_constant_override("separation", 10)
	ui_layer.add_child(bottom_hbox) # Add container to CanvasLayer

	# --- CREATE PLAY/PAUSE BUTTON ---
	play_pause_button = Button.new()
	play_pause_button.text = "⏸" # Initial state is playing, use Pause symbol
	# Use size flags instead of fixed size for better scalability
	play_pause_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	play_pause_button.add_theme_font_size_override("font_size", UI_BUTTON_FONT_SIZE)
	# Connect signal
	play_pause_button.pressed.connect(_toggle_play_pause)
	bottom_hbox.add_child(play_pause_button) # Add to HBoxContainer

	# --- CREATE TIME SLIDER ---
	time_slider = HSlider.new()
	time_slider.min_value = 0.0
	time_slider.max_value = PATH_ANIMATION_DURATION
	time_slider.step = 0.01 # Allow fine control
	time_slider.value = 0.0 # Initial value
	# Make slider expand horizontally to fill available space in HBoxContainer
	time_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	# Set minimum vertical size
	time_slider.custom_minimum_size.y = UI_CONTROL_HEIGHT
	# Connect signals
	time_slider.value_changed.connect(_on_slider_value_changed)
	# Also track dragging state to avoid fighting between _process and user input
	time_slider.drag_started.connect(func(): is_slider_dragging = true)
	time_slider.drag_ended.connect(func(_value_is_final): is_slider_dragging = false)
	bottom_hbox.add_child(time_slider) # Add to HBoxContainer

	print("UI setup complete.")


## Called every frame. Delta is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	# 1. Handle Time Progression if Playing
	if is_playing:
		time_elapsed += delta
		# Check for end of animation
		if time_elapsed >= PATH_ANIMATION_DURATION:
			time_elapsed = PATH_ANIMATION_DURATION
			is_playing = false # Stop playing
			if play_pause_button: play_pause_button.text = "▶" # Use Play symbol

		# Update slider position smoothly ONLY if user isn't dragging it
		if time_slider and not is_slider_dragging:
			time_slider.set_value_no_signal(time_elapsed)

	# 2. Update PathFollower position based on time_elapsed
	if is_instance_valid(path_follow_node):
		var progress_ratio = 0.0
		if PATH_ANIMATION_DURATION > 0.0:
			progress_ratio = clampf(time_elapsed / PATH_ANIMATION_DURATION, 0.0, 1.0)
		path_follow_node.progress_ratio = progress_ratio
		
		# Update the clock's active state based on the main playing state
		if is_instance_valid(clock_assembly_instance):
			clock_assembly_instance.is_active = is_playing
	else:
		printerr("_process: PathFollowNode is not valid!")


# --- Input Handling ---
func _unhandled_input(event: InputEvent) -> void:
	# Check for spacebar press (default mapped to ui_accept)
	if event.is_action_pressed("ui_accept"):
		_toggle_play_pause()
		get_viewport().set_input_as_handled() # Mark event as handled
	# Check for Escape key press (default mapped to ui_cancel)
	elif event.is_action_pressed("ui_cancel"):
		get_tree().quit() # Quit the application
		# No need to mark as handled, as quitting stops further processing

# --- Signal Handlers ---
## Toggles the play/pause state and updates the button text.
## Called by button press and spacebar input.
func _toggle_play_pause() -> void:
	is_playing = not is_playing # Toggle state
	if is_playing:
		if play_pause_button: play_pause_button.text = "⏸" # Use Pause symbol
		# If user paused exactly at the end, reset to beginning to play again
		if time_elapsed >= PATH_ANIMATION_DURATION:
			time_elapsed = 0.0
	else:
		if play_pause_button: play_pause_button.text = "▶" # Use Play symbol

func _on_slider_value_changed(new_value: float) -> void:
	# Only update time if the user is actually dragging
	if is_slider_dragging:
		time_elapsed = new_value
		# When scrubbing, ensure playback state doesn't change unexpectedly
		if time_elapsed >= PATH_ANIMATION_DURATION and is_playing:
			is_playing = false
			if play_pause_button: play_pause_button.text = "▶" # Use Play symbol
		# Note: _process will handle updating the path follower position based on the new time_elapsed
