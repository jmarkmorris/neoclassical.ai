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
const BOUNDS_Y_MAX: float = 7.625  # 5.0 + 2.625 # Keep bounds for initial placement/containment? Or remove? Let's keep for now.

# Physics Parameters
const INITIAL_POS_SPREAD: float = 2.0 # Spread for initial random positions around center
const INITIAL_VEL_MAGNITUDE: float = 1.0 # Initial speed magnitude for particles
const SPEED_OF_POTENTIAL: float = 1.0 # Speed at which interaction propagates (set equal to initial speed as requested)
const COULOMB_CONSTANT: float = 5.0 # Strength of attraction/repulsion force
const MIN_DISTANCE_SQ: float = 0.01 # Minimum distance squared to prevent division by zero/huge forces
const PARTICLE_MASS: float = 1.0 # Mass of particles (affects acceleration)
const MAX_HISTORY_SECONDS: float = 5.0 # How many seconds of position history to store
const HISTORY_POINTS_PER_SECOND: int = 30 # How many points per second to store in history


# --- Scene Variables ---
# var path_followers: Array[PathFollow3D] = [] # No longer needed
var trail_mesh_instances: Array[MeshInstance3D] = [] # Nodes to hold the trail meshes
var trail_meshes: Array[ImmediateMesh] = []   # The actual ImmediateMesh resources
var trail_materials: Array[StandardMaterial3D] = [] # To store trail materials
var trail_points: Array[PackedVector3Array] = [] # To store points for each trail
var particle_meshes: Array[MeshInstance3D] = [] # To easily access particle positions

# Particle Physics State
var particle_velocities: Array[Vector3] = []
var particle_charges: Array[float] = [] # +1.0 for Red, -1.0 for Blue
var particle_histories: Array[Array] = [] # Array of arrays, each inner array stores [timestamp, position] pairs

var current_time: float = 0.0 # Keep track of simulation time for history


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

	# 5. Particle Instantiation and Physics State Initialization
	var center_pos = Vector3(0, 1.625, 0) # Use the previous start area center

	for config in PARTICLE_CONFIGS:
		# --- Create Particle Mesh (Same as before) ---
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

		# --- Initialize Physics State ---
		# Random initial position around the center
		var random_offset = Vector3(randf_range(-INITIAL_POS_SPREAD, INITIAL_POS_SPREAD),
									randf_range(-INITIAL_POS_SPREAD, INITIAL_POS_SPREAD),
									0) # Keep Z=0 for 2D-like movement
		particle_mesh_instance.position = center_pos + random_offset
		add_child(particle_mesh_instance) # Add mesh directly to scene now

		# Random initial velocity
		var random_angle = randf_range(0, TAU)
		var initial_velocity = Vector3(cos(random_angle), sin(random_angle), 0) * INITIAL_VEL_MAGNITUDE
		particle_velocities.append(initial_velocity)

		# Assign charge based on color
		var charge = 1.0 if config["object_color"] == PURE_RED else -1.0
		particle_charges.append(charge)

		# Initialize empty history
		particle_histories.append([])
		# Add initial state to history
		particle_histories[-1].append([0.0, particle_mesh_instance.position])

		# Store mesh reference (needed for position access and trail)
		particle_meshes.append(particle_mesh_instance)

		# --- Create Trail Rendering Components (Mostly same as before) ---
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

	# 7. Animation Setup - REMOVED


# Helper function to find historical position via interpolation
func _get_historical_position(history: Array, target_time: float) -> Vector3:
	if history.is_empty():
		push_error("History is empty, cannot get historical position.")
		return Vector3.ZERO # Should not happen if initialized correctly
	if target_time <= history[0][0]: # Requesting time before first record
		return history[0][1]
	if target_time >= history[-1][0]: # Requesting time after last record
		return history[-1][1]

	# Binary search or linear scan to find points bracketing target_time
	# Linear scan is simpler for potentially short histories
	for i in range(history.size() - 1):
		var time1: float = history[i][0]
		var pos1: Vector3 = history[i][1]
		var time2: float = history[i+1][0]
		var pos2: Vector3 = history[i+1][1]

		if target_time >= time1 and target_time <= time2:
			if time1 == time2: # Avoid division by zero if timestamps are identical
				return pos1
			# Interpolate
			var t = (target_time - time1) / (time2 - time1)
			return pos1.lerp(pos2, t)

	# Should be unreachable if checks above are correct, but return last known as fallback
	push_warning("Could not find bracketing time in history for interpolation.")
	return history[-1][1]


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	current_time += delta
	var num_particles = particle_meshes.size()
	var forces: Array[Vector3] = [] # Array to store total force on each particle for this frame
	forces.resize(num_particles)
	forces.fill(Vector3.ZERO)

	# 1. Calculate Forces using Historical Positions
	for i in range(num_particles): # Receiver particle
		var receiver_pos: Vector3 = particle_meshes[i].global_transform.origin
		var receiver_charge: float = particle_charges[i]

		for j in range(num_particles): # Emitter particle
			if i == j: continue # Particle doesn't interact with itself

			var emitter_charge: float = particle_charges[j]
			var emitter_history: Array = particle_histories[j]

			# Estimate distance to get approximate time delay
			# Using current distance is an approximation, but needed to query history
			var approx_dist = receiver_pos.distance_to(particle_meshes[j].global_transform.origin)
			var time_delay = approx_dist / SPEED_OF_POTENTIAL
			var historical_time = current_time - time_delay

			# Get emitter's position at that historical time
			var emitter_historical_pos = _get_historical_position(emitter_history, historical_time)

			# Calculate force based on historical position
			var vec_to_emitter = emitter_historical_pos - receiver_pos
			var dist_sq = vec_to_emitter.length_squared()

			# Clamp distance to avoid extreme forces at close range
			dist_sq = max(dist_sq, MIN_DISTANCE_SQ)

			# Calculate Coulomb-like force: F = k * q1 * q2 / r^2 * direction
			# Negative sign because q1*q2 is negative for attraction, positive for repulsion
			# We want force vector pointing *away* from emitter for repulsion, *towards* for attraction
			var force_magnitude = COULOMB_CONSTANT * receiver_charge * emitter_charge / dist_sq
			var force_direction = vec_to_emitter.normalized()
			var force_on_i = -force_direction * force_magnitude # The negative handles attraction/repulsion correctly

			forces[i] += force_on_i

	# 2. Update Velocities and Positions (Simple Euler integration)
	for i in range(num_particles):
		var acceleration = forces[i] / PARTICLE_MASS
		particle_velocities[i] += acceleration * delta
		particle_meshes[i].global_transform.origin += particle_velocities[i] * delta

	# 3. Record History (Store current state after position update)
	var history_interval = 1.0 / HISTORY_POINTS_PER_SECOND
	for i in range(num_particles):
		var history: Array = particle_histories[i]
		# Add point if enough time has passed since last record or if history is empty
		if history.is_empty() or current_time - history[-1][0] >= history_interval:
			history.append([current_time, particle_meshes[i].global_transform.origin])

			# Prune old history
			var oldest_allowed_time = current_time - MAX_HISTORY_SECONDS
			while history.size() > 1 and history[0][0] < oldest_allowed_time:
				history.pop_front() # Remove oldest entry

	# 4. Update Trail Rendering (Using the NEW current position)
	for i in range(num_particles):
		var particle_mesh: MeshInstance3D = particle_meshes[i]
		var trail_immediate_mesh: ImmediateMesh = trail_meshes[i] # Get the mesh resource
		var points: PackedVector3Array = trail_points[i]
		var material: StandardMaterial3D = trail_materials[i]

		# Get current particle position (already updated by physics)
		var current_pos: Vector3 = particle_mesh.global_transform.origin

		# Add point to trail if it's different from the last one (or if it's the first)
		# Use the default tolerance for is_equal_approx
		if points.is_empty() or not points[-1].is_equal_approx(current_pos):
			points.append(current_pos)

		# Redraw the trail using ImmediateMesh resource
		trail_immediate_mesh.clear_surfaces()
		if points.size() > 1: # Need at least two points to draw a line
			trail_immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP, material)
			for point in points:
				trail_immediate_mesh.surface_add_vertex(point)
			trail_immediate_mesh.surface_end()
