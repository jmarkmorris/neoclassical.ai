extends Node3D

# Configuration
const FONT_DIR_PATH: String = "res://fonts/"
const DISPLAY_TEXT: String = "The quick brown fox jumps over the lazy dog."
const FONT_SIZE: int = 24
# Decreased pixel size for potentially better resolution
const PIXEL_SIZE: float = 0.005
# Adjusted start Y and spacing slightly due to smaller pixel size
const START_Y: float = 1.5
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
	var label_count: int = 0

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

					# Position the label vertically
					label.position.y = START_Y - (label_count * VERTICAL_SPACING)
					label.position.x = 0.0 # Center horizontally

					# Add to the scene
					add_child(label)
					label_count += 1
					# Optional: break here if you only expect one .tres per folder
					# break
				elif resource:
					printerr("FontDisplayManager: Resource is not a Font: ", resource_path)
				else:
					printerr("FontDisplayManager: Failed to load resource: ", resource_path)

		# font_dir goes out of scope and closes here

	if label_count == 0:
		print("FontDisplayManager: No .tres font files found or loaded in subdirectories of ", FONT_DIR_PATH)
	else:
		print("FontDisplayManager: Finished. Loaded %d fonts." % label_count)

	# base_dir goes out of scope and closes here
