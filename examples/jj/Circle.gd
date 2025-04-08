extends MeshInstance3D

var circle_radius: float = 0.1
var circle_color: Color = Color.WHITE
var material = StandardMaterial3D.new()

func _ready():
    # Create a cylinder mesh with minimal height to appear as a circle
    mesh = CylinderMesh.new()
    update_properties()

func set_circle_properties(new_radius: float, new_color: Color):
    circle_radius = new_radius
    circle_color = new_color
    update_properties()

func update_properties():
    mesh.top_radius = circle_radius
    mesh.bottom_radius = circle_radius
    mesh.height = 0.01
    
    material.albedo_color = circle_color
    material.roughness = 0.2
    set_surface_override_material(0, material)
