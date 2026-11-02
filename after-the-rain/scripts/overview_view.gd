extends Node3D
## Independent authored camera, never relocates the player or mutates reader state.
@onready var camera: Camera3D = $Camera3D
var active := false
var _previous: WeakRef

func begin() -> bool:
	if active: return false
	var previous := get_viewport().get_camera_3d()
	_previous = weakref(previous) if is_instance_valid(previous) and previous != camera else null
	active = true
	camera.make_current()
	return true

func end() -> void:
	if not active: return
	active = false
	if camera.is_current():
		var previous: Camera3D = _previous.get_ref() if _previous != null else null
		camera.clear_current(false)
		if is_instance_valid(previous) and previous.is_inside_tree(): previous.make_current()
	_previous = null

func reset() -> void:
	end()

func _exit_tree() -> void:
	end()
