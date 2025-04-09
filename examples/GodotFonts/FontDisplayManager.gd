extends Node3D

# Configuration
const FONT_DIR_PATH: String = "res://fonts/"
const DISPLAY_TEXT: String = "The quick brown fox jumps over the lazy dog."
const FONT_SIZE: int = 32
# Decreased pixel size for potentially better resolution
const PIXEL_SIZE: float = 0.006
# Adjusted start Y and spacing slightly due to smaller pixel size
const START_Y: float = .5
const VERTICAL_SPACING: float = 0.35

func _ready() -> void:
	print("FontDisplayManager: Starting font loading...")
	_load_and_display_fonts()

func _load_and_display_fonts() -> void:
	# Ensure the path is absolute and print it for debugging
	var absolute_path: String = ProjectSettings.globalize_path(FONT_DIR_PATH)
	print("FontDisplayManager: Attempting to open base font directory: ", absolute_path)

	var base_dir = DirAccess.open(absolute_path)
	if not base_dir:
		printerr("FontDisplayManager: Failed to open base directory: ", absolute_path)
		return

	var font_dirs: PackedStringArray = base_dir.get_directories()
	var created_labels: Array[Label3D] = [] # Array to hold labels before positioning

	print("FontDisplayManager: Found font directories: ", font_dirs)

	for font_dir_name in font_dirs:
		var font_subdir_path: String = FONT_DIR_PATH.path_join(font_dir_name)
		print("FontDisplayManager: Checking directory: ", font_subdir_path)

		var font_dir = DirAccess.open(font_subdir_path)
		if not font_dir:
			printerr("FontDisplayManager: Failed to open font subdirectory: ", font_subdir_path)
			continue # Skip to the next directory

		var files_in_subdir: PackedStringArray = font_dir.get_files()

		for file_name in files_in_subdir:
			if file_name.ends_with(".tres"):
				var resource_path: String = font_subdir_path.path_join(file_name)
				print("FontDisplayManager: Attempting to load: ", resource_path)

				var resource = load(resource_path)

				if resource and resource is Font:
					print("FontDisplayManager: Successfully loaded font: ", file_name, " from ", font_dir_name)
					var font: Font = resource as Font

					var label: Label3D = Label3D.new()

					# Assign font and size directly
					label.font = font
					label.font_size = FONT_SIZE

					# Configure the label text, alignment, etc.
					# Include the directory name in the label for clarity
					label.text = "%s (%s/%s)" % [DISPLAY_TEXT, font_dir_name, file_name]
					label.pixel_size = PIXEL_SIZE
					label.billboard = BaseMaterial3D.BILLBOARD_ENABLED # Make it face the camera
					label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER # Center the text
					label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER # Center the text vertically
					label.outline_size = 0 # Explicitly disable outline via script

					# Add to the scene and store for later positioning
					add_child(label)
					created_labels.append(label)
					# Optional: break here if you only expect one .tres per folder
					# break
				elif resource:
					printerr("FontDisplayManager: Resource is not a Font: ", resource_path)
				else:
					printerr("FontDisplayManager: Failed to load resource: ", resource_path)

		# font_dir goes out of scope and closes here

	# --- Positioning Phase ---
	var label_count: int = created_labels.size()
	if label_count == 0:
		print("FontDisplayManager: No .tres font files found or loaded in subdirectories of ", FONT_DIR_PATH)
	else:
		print("FontDisplayManager: Positioning %d loaded fonts." % label_count)

		# Calculate total height and starting position for vertical centering
		var total_block_height: float = float(label_count) * VERTICAL_SPACING

		# Adjust start_y to center the block around y=0
		# Subtract half a spacing to center the lines themselves, not the gaps
		var actual_start_y: float = (total_block_height / 2.0) - (VERTICAL_SPACING / 2.0)

		# Define the upward shift amount (adjust this value as needed)
		var vertical_shift: float = 1.0 # Adjust this value to control the shift

		# Position each label
		for i in range(label_count):
			var label: Label3D = created_labels[i]
			# Calculate base centered position and add the shift
			label.position.y = (actual_start_y - (i * VERTICAL_SPACING)) + vertical_shift
			label.position.x = 0.0 # Center horizontally

		print("FontDisplayManager: Finished positioning with vertical shift.")

	# base_dir goes out of scope and closes here
