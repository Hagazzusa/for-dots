extends Node3D
## One distant authored pane. Coordinator injects the shared evening elapsed time.
@export_range(1.0, 600.0) var cycle_seconds := 160.0
@export var lamp_on_start := 12.0
@export var lamp_on_fade := 6.0
@export var lamp_off_start := 72.0
@export var lamp_off_fade := 6.0
@export var crossing_start := 38.0
@export var crossing_seconds := 9.0
@onready var pane: MeshInstance3D = $Pane
var material: ShaderMaterial
var phase := 0.0
var lamp_strength := 0.0
var silhouette_progress := 0.0
var silhouette_strength := 0.0

func _ready() -> void:
	material = pane.material_override.duplicate()
	pane.material_override = material
	reset()

func reset() -> void:
	present(0.0)

func present(elapsed: float) -> void:
	if not is_finite(elapsed): return
	var cycle := maxf(cycle_seconds,1.0)
	phase = fposmod(maxf(elapsed,0.0),cycle)
	var on_start := clampf(lamp_on_start,0.0,cycle-0.003)
	var on_end := clampf(on_start+maxf(lamp_on_fade,0.001),on_start+0.001,cycle-0.002)
	var off_start := clampf(lamp_off_start,on_end,cycle-0.001)
	var off_end := clampf(off_start+maxf(lamp_off_fade,0.001),off_start+0.001,cycle)
	lamp_strength = smoothstep(on_start,on_end,phase)*(1.0-smoothstep(off_start,off_end,phase))
	silhouette_progress = clampf((phase-crossing_start)/maxf(crossing_seconds,0.001),0.0,1.0)
	silhouette_strength = lamp_strength*smoothstep(0.0,0.12,silhouette_progress)*(1.0-smoothstep(0.88,1.0,silhouette_progress))
	pane.visible = lamp_strength > 0.0
	material.set_shader_parameter("lamp_strength",lamp_strength)
	material.set_shader_parameter("silhouette_progress",silhouette_progress)
	material.set_shader_parameter("silhouette_strength",silhouette_strength)
