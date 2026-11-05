extends Node3D
## A scene-local camera attachment. Rain cover and interaction belong to the session.
signal state_changed(held: bool, is_open: bool)

@export_range(0.0, 0.025) var sway_amount: float = 0.008
@export_range(1.0, 12.0) var settle_speed: float = 5.0
var held: bool = false
var is_open: bool = false
var _rest: Transform3D
var _phase: float = 0.0
@onready var open_canopy: Node3D = $OpenCanopy
@onready var folded_canopy: Node3D = $FoldedCanopy

func _ready() -> void:
	_rest = transform
	reset()

func borrow() -> void:
	if held:
		return
	held = true
	is_open = false
	_sync_visuals()
	state_changed.emit(held, is_open)

func toggle_open() -> void:
	if not held:
		return
	is_open = not is_open
	_sync_visuals()
	state_changed.emit(held, is_open)

func return_umbrella() -> void:
	reset()

func reset() -> void:
	var changed := held or is_open
	held = false
	is_open = false
	_phase = 0.0
	transform = _rest
	_sync_visuals()
	if changed:
		state_changed.emit(false, false)

func present(delta: float, velocity: Vector3) -> void:
	if not held:
		return
	var dt := maxf(delta, 0.0)
	_phase = fmod(_phase + dt * 3.2, TAU)
	var motion := clampf(Vector2(velocity.x, velocity.z).length() / 2.4, 0.0, 1.0)
	var offset := Vector3(sin(_phase) * sway_amount, sin(_phase * 2.0) * sway_amount * 0.5, 0.0) * motion
	position = position.lerp(_rest.origin + offset, 1.0 - exp(-settle_speed * dt))
	# No world-space rotation: looking up/down cannot swing the canopy through the camera or cocoa.

func _sync_visuals() -> void:
	visible = held
	open_canopy.visible = is_open
	folded_canopy.visible = not is_open
