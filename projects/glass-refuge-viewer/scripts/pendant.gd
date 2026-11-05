extends Node3D
## Owns lamp state. Composition root injects the source-derived globe mesh.
signal changed(is_on: bool)
@export var on_energy := 2.8
var is_on := true
var globe_material: StandardMaterial3D
@onready var light: OmniLight3D = $Light

func bind_globe(mesh: MeshInstance3D) -> void:
	assert(mesh != null)
	globe_material = StandardMaterial3D.new()
	globe_material.resource_local_to_scene = true
	globe_material.roughness = 0.3
	mesh.material_override = globe_material
	set_on(is_on)

func set_on(value: bool) -> void:
	is_on = value
	light.visible = value
	light.light_energy = on_energy if value else 0.0
	if globe_material:
		globe_material.albedo_color = Color(1.0, 0.76, 0.43) if value else Color(0.62, 0.64, 0.65)
		globe_material.emission_enabled = value
		globe_material.emission = Color(1.0, 0.58, 0.22)
		globe_material.emission_energy_multiplier = 1.4 if value else 0.0
	changed.emit(value)
