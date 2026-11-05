extends Node3D
## Existing tuner surface only. The composition root supplies radio power state.
@export var lit_material: StandardMaterial3D = preload("res://assets/materials/radio_dial_lit.tres")
@onready var tuner: MeshInstance3D = $Tuner
var powered := false
var _off_material: Material
var _on_material: Material

func _ready() -> void:
 _off_material = tuner.material_override.duplicate()
 _on_material = lit_material.duplicate() if lit_material != null else _off_material
 set_powered(powered)

func set_powered(value: bool) -> void:
 powered = value
 if is_node_ready():
  tuner.material_override = _on_material if powered else _off_material
