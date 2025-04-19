extends Node3D

# --- Constants ---

# Define Colors
const INDIGO: Color = Color("#4B0082")
const PURE_BLUE: Color = Color("#0000FF")
const PURE_RED: Color = Color("#FF0000")
const LIGHT_BLUE: Color = Color("#ADD8E6") # Or BLUE_C from Manim: Color("#58C4DD")
const LIGHT_RED: Color = Color("#FFC0CB")  # Or RED_C from Manim: Color("#FC6255")

# Particle Properties
const PARTICLE_RADIUS: float = 0.1 # Adjusted from Manim's 0.075 for visibility
const NUM_PARTICLES_PER_COLOR: int = 3

# Particle Configurations (Object Color, Trail Color)
const PARTICLE_CONFIGS: Array[Dictionary] = [
	{"object_color": PURE_BLUE, "trail_color": LIGHT_BLUE},
	{"object_color": PURE_BLUE, "trail_color": LIGHT_BLUE},
	{"object_color": PURE_BLUE, "trail_color": LIGHT_BLUE},
	{"object_color": PURE_RED, "trail_color": LIGHT_RED},
	{"object_color": PURE_RED, "trail_color": LIGHT_RED},
	{"object_color": PURE_RED, "trail_color": LIGHT_RED}
]

# Screen Boundaries (adjust as needed based on camera view) - Moved Up 15%
const BOUNDS_X_MIN: float = -14.0
const BOUNDS_X_MAX: float = 14.0
const BOUNDS_Y_MIN: float = -9.875 # -12.5 + 2.625
const BOUNDS_Y_MAX: float = 7.625  # 5.0 + 2.625

# Path Generation Parameters
const PATH_START_POS: Vector3 = Vector3(0, 1.625, 0) # -1.0 + 2.625
const PATH_NUM_POINTS: int = 512 # Increased from 256 for smoother paths
const PATH_STEP_SIZE: float = 0.8 # Controls distance between points - Decreased from 1.2


# --- Helper Functions ---

# Generates a random 3D path within specified boundaries
func generate_random_path(start_pos: Vector3, num_points: int, step_size: float,
						  x_min: float, x_max: float, y_min: float, y_max: float) -> Curve3D:
	var curve := Curve3D.new()
	curve.add_point(start_pos)
	var current_point := start_pos
	# var previous_angle: float = randf_range(0, TAU) # No longer needed

	for i in range(num_points):
		var attempts := 0
		while attempts < 10: # Prevent infinite loops if bounds are too tight
			# Calculate new angle completely randomly
			var current_angle: float = randf_range(0, TAU) # Random angle (0 to 2*PI)

			var offset := Vector3(cos(current_angle), sin(current_angle), 0) * step_size
			var next_point := current_point + offset

			# Check bounds
			if (next_point.x >= x_min and next_point.x <= x_max and
				next_point.y >= y_min and next_point.y <= y_max):
				curve.add_point(next_point)
				current_point = next_point
				# previous_angle = current_angle # No longer needed
				break # Valid point found, exit while loop
			else:
				# If boundary hit, try a new random angle
				# previous_angle = randf_range(0, TAU) # No longer needed
				attempts += 1
		if attempts >= 10:
			push_warning("Could not find a valid point within bounds after 10 attempts for point %d. Path might be shorter." % (i + 1))
			# Optionally, just add the last valid point again or stop generation
			# curve.add_point(current_point) # Repeat last point if stuck

	# Bake the curve for smoother interpolation between generated points
	curve.bake_interval = 0.1 # Lower values = smoother curve - Adjusted from 0.05

	return curve


# --- Scene Variables ---
var path_followers: Array[PathFollow3D] = [] # To store references for animation
var trail_mesh_instances: Array[MeshInstance3D] = [] # Nodes to hold the trail meshes
var trail_meshes: Array[ImmediateMesh] = []   # The actual ImmediateMesh resources
var trail_materials: Array[StandardMaterial3D] = [] # To store trail materials
var trail_points: Array[PackedVector3Array] = [] # To store points for each trail
var particle_meshes: Array[MeshInstance3D] = [] # To easily access particle positions


# --- Scene Setup ---

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Initialize Random Number Generator (optional but good practice for reproducibility if needed)
	# seed(42) # Uncomment for deterministic paths like Manim example

	# 1. Camera Setup
	var camera := Camera3D.new()
	camera.position = Vector3(0, 0, 15) # Position the camera
	camera.look_at(Vector3.ZERO)       # Make it look towards the origin
	add_child(camera)
	camera.current = true              # Make this the active camera

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
	label_settings.font_size = 72 # Doubled font size
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

	# Adjust top margin dynamically based on viewport height
	var viewport_height = get_viewport().size.y
	title_label.offset_top = viewport_height * 0.10 # 10% from the top edge
	# Adjust bottom offset based on new font size to ensure it has space
	title_label.offset_bottom = title_label.offset_top + label_settings.font_size * 1.2 # Approximate height

	canvas_layer.add_child(title_label)

	# 5. Particle and Path Instantiation
	for config in PARTICLE_CONFIGS:
		# Create Particle Mesh
		var particle_mesh_instance := MeshInstance3D.new()
		var sphere_mesh := SphereMesh.new()
		sphere_mesh.radius = PARTICLE_RADIUS
		sphere_mesh.height = PARTICLE_RADIUS * 2
		particle_mesh_instance.mesh = sphere_mesh

		# Create Particle Material
		var particle_material := StandardMaterial3D.new()
		particle_material.albedo_color = config["object_color"]
		# Optional: Make particles emissive/unshaded if lighting is distracting
		# particle_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
		particle_mesh_instance.material_override = particle_material # Use override for simplicity

		# Generate Path
		var path_curve: Curve3D = generate_random_path(
			PATH_START_POS,
			PATH_NUM_POINTS,
			PATH_STEP_SIZE,
			BOUNDS_X_MIN, BOUNDS_X_MAX, BOUNDS_Y_MIN, BOUNDS_Y_MAX
		)

		# Create Path Node
		var path_node := Path3D.new()
		path_node.curve = path_curve
		add_child(path_node) # Add the path itself to the scene

		# Create Path Follow Node
		var path_follow_node := PathFollow3D.new()
		# path_follow_node.target = path_node # This is incorrect in Godot 4
		# PathFollow3D needs to be a child of Path3D
		path_node.add_child(path_follow_node) # Make follower a child of the path

		# Add Particle Mesh to Path Follower
		path_follow_node.add_child(particle_mesh_instance)

		# Store references for animation and trail updates
		path_followers.append(path_follow_node)
		particle_meshes.append(particle_mesh_instance) # Store particle mesh ref

		# Create Trail Rendering Components
		var trail_immediate_mesh := ImmediateMesh.new() # Create the mesh resource
		var trail_mesh_node := MeshInstance3D.new()    # Create the node to display it
		trail_mesh_node.mesh = trail_immediate_mesh     # Assign the resource to the node
		add_child(trail_mesh_node)                      # Add the NODE to the scene

		var trail_material := StandardMaterial3D.new()
		trail_material.albedo_color = config["trail_color"]
		trail_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED # Trails look better unshaded
		# Optional: Add transparency
		# trail_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		# trail_material.albedo_color.a = 0.5 # 50% opacity
		trail_mesh_node.material_override = trail_material # Apply material to the node

		trail_mesh_instances.append(trail_mesh_node) # Store the node if needed later
		trail_meshes.append(trail_immediate_mesh)    # Store the mesh resource for updating
		trail_materials.append(trail_material)       # Store the material (used in _process)
		trail_points.append(PackedVector3Array())    # Initialize empty point array for this trail

	# 7. Animation Setup
	var animation_player := AnimationPlayer.new()
	add_child(animation_player)

	var animation := Animation.new()
	animation.length = 60.0 # Animation duration in seconds - Doubled from 30.0

	for i in range(path_followers.size()):
		var follower: PathFollow3D = path_followers[i]
		# Create a unique path to the node for the animation track
		var node_path: NodePath = get_path_to(follower)

		# Add track for progress_ratio
		var track_idx: int = animation.add_track(Animation.TYPE_VALUE)
		animation.track_set_path(track_idx, str(node_path) + ":progress_ratio")

		# Insert keyframes: start at 0, end at 1
		animation.track_insert_key(track_idx, 0.0, 0.0) # time=0, value=0
		animation.track_insert_key(track_idx, animation.length, 1.0) # time=60, value=1

	# Add the animation to the player and play it
	var anim_lib := AnimationLibrary.new()
	anim_lib.add_animation("move_particles", animation)
	animation_player.add_animation_library("", anim_lib) # Add library with empty prefix
	animation_player.play("move_particles")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	# 6. Update Trail Rendering
	for i in range(particle_meshes.size()):
		var particle_mesh: MeshInstance3D = particle_meshes[i]
		var trail_immediate_mesh: ImmediateMesh = trail_meshes[i] # Get the mesh resource
		var points: PackedVector3Array = trail_points[i]
		var material: StandardMaterial3D = trail_materials[i]

		# Get current particle position
		var current_pos: Vector3 = particle_mesh.global_transform.origin

		# Add point to trail if it's different from the last one (or if it's the first)
		if points.is_empty() or not points[-1].is_equal_approx(current_pos):
			points.append(current_pos)

		# Redraw the trail using ImmediateMesh resource
		trail_immediate_mesh.clear_surfaces()
		if points.size() > 1: # Need at least two points to draw a line
			trail_immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP, material)
			for point in points:
				trail_immediate_mesh.surface_add_vertex(point)
			trail_immediate_mesh.surface_end()
