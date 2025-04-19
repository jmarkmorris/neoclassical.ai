extends Node3D

# Define Colors
const INDIGO: Color = Color("#4B0082")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# 1. Camera Setup
	var camera := Camera3D.new()
	camera.position = Vector3(0, 0, 15) # Position the camera
	camera.look_at(Vector3.ZERO)       # Make it look towards the origin
	add_child(camera)
	get_viewport().set_camera_3d(camera) # Make this the active camera

	# 2. Environment Setup
	var world_env := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = INDIGO
	world_env.environment = env
	add_child(world_env)

	# 3. Lighting Setup
	var light := DirectionalLight3D.new()
	light.position = Vector3(5, 5, 5) # Position the light source
	light.look_at(Vector3.ZERO)      # Point the light towards the origin
	add_child(light)

	# 4. Title Setup (using CanvasLayer for 2D overlay)
	var canvas_layer := CanvasLayer.new()
	add_child(canvas_layer)

	var title_label := Label.new()
	title_label.text = "Path Tracing Animation"
	# Note: Font and exact size might need adjustment after importing a font resource.
	# Using theme defaults for now. Let's set a reasonable font size.
	# title_label.add_theme_font_size_override("font_size", 36) # Requires Godot 4.1+
	# For Godot 4.0 compatibility or if themes are preferred:
	var label_settings = LabelSettings.new()
	label_settings.font_size = 36
	title_label.label_settings = label_settings

	# Center the label horizontally and place it near the top
	title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	# Anchors define the control's bounding box relative to its parent.
	# Set anchors for full width, margins for padding.
	title_label.anchor_left = 0.0
	title_label.anchor_right = 1.0
	title_label.anchor_top = 0.0
	title_label.anchor_bottom = 0.0 # Anchor only to top
	# Adjust top margin for padding from the edge
	title_label.offset_top = 20 # Pixels from the top edge
	title_label.offset_bottom = 60 # Define a nominal height for the label area

	canvas_layer.add_child(title_label)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
