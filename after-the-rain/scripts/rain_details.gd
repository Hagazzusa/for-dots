extends Node3D
## Decorative deterministic rain detail only; session supplies its shared clock.
@export var ripple_period := 2.8
@export_range(0.0,1.0,0.01) var ripple_opacity := 0.16
@export var drop_cycle := 1.44
@export var drop_flight := 0.76
@export var outlet_height := 2.98
@export var impact_height := 0.103
@export var drop_spread := 0.02
@export var drop_opacity := 0.48
@export var lull_drop_opacity := 0.22
var elapsed := 0.0
var phase := 0.0
var lull := 0.0
var active_drop_count := 0
var drop_positions: Array[Vector3] = []
var drop_active: Array[bool] = []
var _ripple_materials: Array[ShaderMaterial] = []
var _drop_material: StandardMaterial3D
var _impact_material: ShaderMaterial
@onready var drops: MultiMeshInstance3D = $Gutter/Drops

func _ready() -> void:
	for plane in $Puddles.get_children():
		var material := plane.material_override.duplicate() as ShaderMaterial
		plane.material_override = material
		_ripple_materials.append(material)
	_impact_material = $Gutter/Impact.material_override.duplicate() as ShaderMaterial
	$Gutter/Impact.material_override = _impact_material
	_drop_material = drops.material_override.duplicate() as StandardMaterial3D
	drops.material_override = _drop_material
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = drops.multimesh.mesh
	mm.instance_count = 12
	drops.multimesh = mm
	drop_positions.resize(12)
	drop_active.resize(12)
	reset()

func present(seconds: float, weather_lull: float) -> void:
	if not is_finite(seconds) or not is_finite(weather_lull): return
	elapsed = maxf(seconds,0.0)
	lull = clampf(weather_lull,0.0,1.0)
	var period := maxf(ripple_period,.01)
	phase = fposmod(elapsed,period)/period
	for i in range(_ripple_materials.size()):
		var local_time := elapsed + i*.371
		var local_phase := fposmod(local_time,period)/period
		var cycle := floorf(local_time/period)
		var center := Vector2(sin(cycle*1.73+i*2.11),cos(cycle*2.31+i*1.37))*.06
		_ripple_materials[i].set_shader_parameter("phase",local_phase)
		_ripple_materials[i].set_shader_parameter("center",center)
		_ripple_materials[i].set_shader_parameter("opacity",ripple_opacity*lerpf(1.0,.58,lull))
	var cycle_length := maxf(drop_cycle,.01)
	var flight := clampf(drop_flight,.001,cycle_length)
	active_drop_count = 0
	for i in range(12):
		var age := fposmod(fposmod(elapsed,cycle_length)+i*cycle_length/12.0,cycle_length)
		var active := age < flight
		var point := Vector3(sin(i*2.399)*drop_spread,lerpf(outlet_height,impact_height+.0225,clampf(age/flight,0.0,1.0)),cos(i*2.399)*drop_spread)
		drop_positions[i] = point
		drop_active[i] = active
		if active: active_drop_count += 1
		drops.multimesh.set_instance_transform(i,Transform3D(Basis().scaled(Vector3.ONE if active else Vector3.ZERO),point))
	var tint := _drop_material.albedo_color
	tint.a = lerpf(drop_opacity,lull_drop_opacity,lull)
	_drop_material.albedo_color = tint
	var impact_age := fposmod(elapsed-flight,cycle_length)
	_impact_material.set_shader_parameter("phase",clampf(impact_age/.5,0.0,1.0))
	_impact_material.set_shader_parameter("opacity",0.20*lerpf(1.0,.58,lull) if impact_age<.5 else 0.0)

func reset() -> void:
	present(0.0,0.0)

## Analytical CPU state used by rendering uploads and headless validation alike.
func get_drop_position(index: int) -> Vector3:
	return drop_positions[index]

func is_drop_active(index: int) -> bool:
	return drop_active[index]
