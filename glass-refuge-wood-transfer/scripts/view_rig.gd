extends Node3D
## Camera-only orbit; never moves the model. No captured mouse or hidden walking mode.
signal view_changed
@export var target := Vector3(0.0, 1.65, 0.0)
@export var orbit_speed := 0.9
@export var zoom_speed := 3.5
var yaw := 0.48
var pitch := 0.20
var distance := 9.3
var dragging := false
@onready var camera: Camera3D = $Camera3D

func _ready() -> void:
	get_window().focus_exited.connect(_stop_drag)
	update_camera()

func _stop_drag() -> void:
	dragging = false

func _process(delta: float) -> void:
	if not get_window().has_focus():
		return
	var focus := get_viewport().gui_get_focus_owner()
	if focus is LineEdit or focus is TextEdit:
		return
	var horizontal := float(key_down(KEY_RIGHT)) - float(key_down(KEY_LEFT))
	var vertical := float(key_down(KEY_UP)) - float(key_down(KEY_DOWN))
	var zoom := float(key_down(KEY_MINUS)) - float(key_down(KEY_EQUAL) or key_down(KEY_PLUS))
	if horizontal != 0.0 or vertical != 0.0 or zoom != 0.0:
		orbit(horizontal * orbit_speed * delta, vertical * orbit_speed * delta)
		zoom_by(zoom * zoom_speed * delta)

func key_down(code: Key) -> bool:
	return Input.is_physical_key_pressed(code) or Input.is_key_pressed(code)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			dragging = event.pressed
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom_by(-0.5)
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom_by(0.5)
	elif event is InputEventMouseMotion and dragging:
		orbit(-event.relative.x * 0.005, event.relative.y * 0.005)

func orbit(horizontal: float, vertical: float) -> void:
	yaw = wrapf(yaw + horizontal, -PI, PI)
	pitch = clampf(pitch + vertical, -0.02, 1.1)
	update_camera()

func zoom_by(amount: float) -> void:
	distance = clampf(distance + amount, 4.3, 15.0)
	update_camera()

func reset_view() -> void:
	yaw = 0.48
	pitch = 0.20
	distance = 9.3
	dragging = false
	update_camera()

func update_camera() -> void:
	camera.position = target + Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * distance
	camera.look_at(target, Vector3.UP)
	view_changed.emit()
