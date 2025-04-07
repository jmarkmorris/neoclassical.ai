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
const PATH_SAMPLE_STEPS: int = 100
const ORTHOGONAL_CAMERA_SIZE: float = 5.0 # Controls the vertical view size
const PATH_ANIMATION_DURATION: float = 15.0
const INITIAL_CLOCK_RADIUS_FACTOR: float = 2.0 * 0.95 * 0.95 # Matches Manim example

# --- Properties ---
## Instance of the clock assembly node.
var clock_assembly_instance: ClockAssembly
## The Path3D node defining the clock's movement trajectory.
var path_node: Path3D
## The PathFollow3D node that moves the clock along the path.
var path_follow_node: PathFollow3D
## Optional MeshInstance3D to visualize the path itself.
var path_visualization_mesh: MeshInstance3D

## Called when the node enters the scene tree for the first time.
## Orchestrates the setup of the entire scene.
func _ready() -> void:
	print("Clock main scene ready.")
	_setup_environment()
	_create_path()
	_create_clock()
	_setup_path_following()
	_start_animation()

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
			PATH_PARAM_X_AMP * sin(t * PATH_PARAM_X_FREQ),
			PATH_PARAM_Y_AMP * cos(t * PATH_PARAM_Y_FREQ),
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
	var path_mesh = ImmediateMesh.new()
	var path_material = StandardMaterial3D.new()
	# Use semi-transparent white for the path, closer to the example image
	path_material.albedo_color = Color(1.0, 1.0, 1.0, 0.5)
	path_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	# Enable transparency for the alpha component of YELLOW_A
	path_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA

	path_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	# Iterate through the baked points of the curve for visualization
	for point in curve.get_baked_points():
		path_mesh.surface_add_vertex(point)
	path_mesh.surface_end()

	path_visualization_mesh.mesh = path_mesh
	path_visualization_mesh.material_override = path_material
	add_child(path_visualization_mesh) # Add visualization directly to the main scene
	print("Added path visualization mesh.")


## Instantiates the ClockAssembly node.
func _create_clock() -> void:
	print("Instantiating ClockAssembly...")
	# Instantiate the ClockAssembly using its class_name
	# Pass the adjusted radius factor defined as a constant
	clock_assembly_instance = ClockAssembly.new(INITIAL_CLOCK_RADIUS_FACTOR)
	clock_assembly_instance.name = "ClockAssemblyInstance"

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


## Starts the animation of the clock moving along the path using a Tween.
func _start_animation() -> void:
	# Ensure the path follower node exists before creating the tween
	if not is_instance_valid(path_follow_node):
		printerr("PathFollow3D node is not valid for starting animation.")
		return

	print("Starting path animation tween...")
	# 1. Create a new Tween
	# SceneTreeTween is automatically bound to the scene lifecycle
	var tween: Tween = create_tween()

	# 2. Configure the Tween
	tween.set_loops() # Make the animation loop indefinitely
	tween.set_trans(Tween.TRANS_LINEAR) # Use linear interpolation for constant speed
	# set_ease(Tween.EASE_IN_OUT) is not needed for TRANS_LINEAR

	# 3. Animate the 'progress_ratio' property
	# This property controls the position along the Path3D (0.0 = start, 1.0 = end)
	# Animate from 0.0 to 1.0 over PATH_ANIMATION_DURATION seconds
	tween.tween_property(path_follow_node, "progress_ratio", 1.0, PATH_ANIMATION_DURATION).from(0.0)

	# The tween starts automatically. No need to call tween.play() for SceneTreeTween

	print("Tween created and started for path following.")
