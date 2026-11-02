extends Node3D
## Explicitly stepped, instance-local procedural population. The saved child
## owns its mesh/material; only transforms/population are procedural.
@export var drop_count := 1400
@export var downward_speed := 8.0
@export var wind_speed := .8
@export var shelter_half_width := 3.6
@export var shelter_half_depth := 1.4
@export var roof_height := 3.15
@export var initial_positions: Array[Vector3] = []
@onready var instances: MultiMeshInstance3D = $Drops
@export var additional_shelters: Array[AABB] = []
var weather_lull := 0.0
var umbrella_center := Vector3.ZERO
var umbrella_cover := false
func set_umbrella_cover(center:Vector3, enabled:bool):
	umbrella_center=center
	umbrella_cover=enabled

var drops: Array[Vector3] = []

func _ready() -> void:
	if not initial_positions.is_empty():
		initialize(initial_positions)
	else:
		# Standalone fallback only. Main injects its baked post-layout RNG draw
		# sequence so the baseline rain retains the exact original seed ordering.
		var rng := RandomNumberGenerator.new()
		rng.seed = 73
		var fallback: Array[Vector3] = []
		for i in range(drop_count):
			fallback.append(Vector3(rng.randf_range(-18,18),rng.randf_range(0,13),rng.randf_range(-8,20)))
		initialize(fallback)

func initialize(positions: Array) -> void:
	drops.clear()
	for p in positions:
		drops.append(p as Vector3)
	var source_mesh := instances.multimesh.mesh
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = source_mesh
	mm.instance_count = drops.size()
	instances.multimesh = mm
	set_weather(weather_lull)
	_update_transforms()

func set_weather(lull: float) -> void:
	weather_lull = clampf(lull, 0.0, 1.0)
	if is_instance_valid(instances) and instances.multimesh:
		instances.multimesh.visible_instance_count = roundi(drops.size() * lerpf(1.0, 0.58, weather_lull))

func advance(delta: float) -> void:
	for i in range(drops.size()):
		var p := drops[i]
		p.y -= delta*downward_speed
		p.x -= delta*wind_speed
		if p.y < .12:
			p.y += 13
		if p.x < -18:
			p.x += 36
		drops[i] = p
	_update_transforms()

func _drop_hidden(p: Vector3) -> bool:
	if absf(p.x)<shelter_half_width and absf(p.z)<shelter_half_depth and p.y<roof_height:
		return true
	for shelter in additional_shelters:
		if shelter.has_point(to_global(p)):
			return true
	return umbrella_cover and p.y<umbrella_center.y+.6 and Vector2(p.x-umbrella_center.x,p.z-umbrella_center.z).length()<.95

func _update_transforms() -> void:
	for i in range(drops.size()):
		var p := drops[i]
		instances.multimesh.set_instance_transform(i,Transform3D(Basis().scaled(Vector3.ZERO if _drop_hidden(p) else Vector3.ONE),p))
