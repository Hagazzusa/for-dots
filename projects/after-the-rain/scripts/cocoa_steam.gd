extends Node3D
## Reconstructed CPU presentation only. Heat/age belongs to DrinkSession.
@onready var wisps: Array[MeshInstance3D] = [$Wisp1, $Wisp2, $Wisp3]
var materials: Array[StandardMaterial3D] = []
var elapsed := 0.0
const CYCLE := 1.6
func _ready() -> void:
	for wisp in wisps:
		var own := wisp.material_override.duplicate() as StandardMaterial3D
		wisp.material_override = own
		materials.append(own)
	reset()
func reset() -> void:
	elapsed = 0.0
	hide()
	for i in range(wisps.size()):
		wisps[i].position = Vector3.ZERO
		materials[i].albedo_color = Color(1, 1, 1, 0)
func advance(delta: float, rim_global: Vector3, show_steam: bool, heat: float, sheltered: bool, covered: bool) -> void:
	elapsed = fmod(elapsed + maxf(delta, 0), CYCLE)
	global_transform = Transform3D(Basis.IDENTITY, rim_global)
	visible = show_steam and heat > 0.0
	var wind := .65 if sheltered else (.25 if covered else 1.0)
	for i in range(wisps.size()):
		var phase := fmod(elapsed / CYCLE + float(i) / 3.0, 1.0)
		var angle := float(i) * TAU / 3.0 + sin(phase * TAU) * .35
		var drift := .055 * phase * wind
		wisps[i].position = Vector3(cos(angle) * drift, .055 + phase * .18, sin(angle) * drift)
		wisps[i].scale = Vector3(.7 + phase * .3, .85 + phase * .15, 1)
		materials[i].albedo_color = Color(1, 1, 1, sin(phase * PI) * clampf(heat, 0, 1) if visible else 0.0)
