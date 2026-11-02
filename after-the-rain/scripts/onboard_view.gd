extends Node3D
## An authored window-side seat. The session owns time and the ending transition.
signal finished

@export_range(1.0, 30.0) var duration: float = 8.0
@export var travel: Vector3 = Vector3(3.0, 0.0, 0.0)
@export_range(0.0, 0.03) var ride_sway: float = 0.006

var elapsed: float = 0.0
var active: bool = false
var _finished_sent: bool = false
var _rest_transform: Transform3D
@onready var camera: Camera3D = $Camera3D

func _ready() -> void:
	_rest_transform = transform
	reset()

func begin() -> void:
	reset()
	active = true
	show()
	camera.make_current()

func advance(delta: float) -> void:
	if not active:
		return
	elapsed = minf(elapsed + maxf(delta, 0.0), duration)
	var progress := clampf(elapsed / maxf(duration, 0.001), 0.0, 1.0)
	# Ease out of the stop; no abrupt camera rotation or intrusive effects.
	position = _rest_transform.origin + travel * progress * progress
	camera.position.y = 1.7 + sin(elapsed * 2.2) * ride_sway * sin(progress * PI)
	if elapsed >= duration and not _finished_sent:
		_finished_sent = true
		active = false
		finished.emit()

func reset() -> void:
	active = false
	elapsed = 0.0
	_finished_sent = false
	transform = _rest_transform
	camera.position = Vector3(0.0, 1.7, 0.0)
	camera.current = false
	hide()
