extends Node3D
## An authored window-side seat. The session owns time and the ending transition.
signal finished

@export_range(1.0, 30.0) var duration: float = 8.0
@export var travel: Vector3 = Vector3(3.0, 0.0, 0.0)
@export_range(0.0, 0.03) var ride_sway: float = 0.006

@export_range(0.0, 0.005) var linger_sway: float = 0.0021
var linger := false
var linger_phase := 0.0
var _camera_rest: Transform3D
var elapsed: float = 0.0
var active: bool = false
var _finished_sent: bool = false
var _rest_transform: Transform3D
@onready var camera: Camera3D = $Camera3D

func _ready() -> void:
	_rest_transform = transform
	_camera_rest = camera.transform
	reset()

func begin() -> void:
	reset()
	active = true
	show()
	camera.make_current()

func advance(delta: float) -> void:
	if not is_finite(delta): return
	if linger:
		linger_phase = fposmod(linger_phase + maxf(delta,0.0)*0.55,TAU)
		position = _rest_transform.origin + travel
		camera.transform = _camera_rest
		camera.position += Vector3(sin(linger_phase)*0.55,sin(linger_phase*2.0)*0.8,0.0)*linger_sway
		return
	if not active:
		return
	elapsed = minf(elapsed + maxf(delta, 0.0), duration)
	var progress := clampf(elapsed / maxf(duration, 0.001), 0.0, 1.0)
	# Ease out of the stop; no abrupt camera rotation or intrusive effects.
	position = _rest_transform.origin + travel * progress * progress
	camera.transform = _camera_rest
	camera.position.y += sin(elapsed * 2.2) * ride_sway * sin(progress * PI)
	if elapsed >= duration and not _finished_sent:
		_finished_sent = true
		active = false
		finished.emit()

func reset() -> void:
	active = false
	elapsed = 0.0
	_finished_sent = false
	transform = _rest_transform
	linger = false
	linger_phase = 0.0
	camera.transform = _camera_rest
	camera.current = false
	hide()

func start_linger() -> bool:
	if not _finished_sent or active or linger: return false
	linger = true
	linger_phase = 0.0
	show()
	camera.transform = _camera_rest
	position = _rest_transform.origin + travel
	camera.make_current()
	return true

func stop_linger() -> void:
	if not linger: return
	linger = false
	linger_phase = 0.0
	position = _rest_transform.origin + travel
	camera.transform = _camera_rest
