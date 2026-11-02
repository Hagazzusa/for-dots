extends Node3D
## Self-contained passenger. Root session supplies bus state and world-space entry.
## Approach offsets are relative to the captured home position, not global paths.
@export var approach_offsets: Array[Vector3] = [Vector3(0, 0, 1.45), Vector3(6.45, 0, 1.45)]
@export_range(0.2, 3.0, 0.05) var walk_speed := 1.15
@export var dialogue_departure_delay := 2.0
@export var door_open_delay := 0.8
@onready var visual: Node3D = $Visual
@onready var solid: StaticBody3D = $Solid
@onready var prompt_sign: Label3D = $Sign
var state := "wait"
var returning := false
var departed := false
@export_range(0.2, 3.0, 0.05) var thanks_duration := 1.6
@export_range(0.0, 0.4, 0.01) var thanks_angle := 0.26
@onready var head_pivot: Node3D = $Visual/HeadPivot
var thanking := false
var thanks_elapsed := 0.0
var _head_rest: Transform3D
var _home: Transform3D
var _layer: int
var _mask: int
var _time := 0.0
var _stop_time := 0.0
var _path: Array[Vector3] = []
var _trail: Array[Vector3] = []

func _ready() -> void:
	_head_rest = head_pivot.transform
	_home = global_transform
	_layer = solid.collision_layer
	_mask = solid.collision_mask
	reset()

func is_available() -> bool:
	return state == "wait" and visible

func reset() -> void:
	global_transform = _home
	state = "wait"
	departed = false
	_cancel_thanks()
	returning = false
	_time = 0.0
	_stop_time = 0.0
	_path.clear()
	_trail.clear()
	visible = true
	visual.transform = Transform3D.IDENTITY
	visual.get_node("LegLeft").rotation.x = 0.0
	visual.get_node("LegRight").rotation.x = 0.0
	prompt_sign.visible = true
	_set_solid(true)

func leave_with_player() -> void:
	_cancel_thanks()
	state = "boarded"
	returning = false
	_path.clear()
	_trail.clear()
	visible = false
	_set_solid(false)

func _set_solid(value: bool) -> void:
	solid.collision_layer = _layer if value else 0
	solid.collision_mask = _mask if value else 0

func _start_walk(boarding_point: Vector3) -> void:
	_cancel_thanks()
	state = "walk"
	returning = false
	_trail.assign([_home.origin])
	_path.clear()
	for offset in approach_offsets:
		_path.append(_home.origin + offset)
	var entry := boarding_point
	entry.y = _home.origin.y
	_path.append(entry)
	_set_solid(false)
	prompt_sign.visible = false

func _return_home() -> void:
	returning = true
	_path.clear()
	# Retrace only reached corners, never cut diagonally through the shelter.
	for i in range(_trail.size() - 1, -1, -1):
		_path.append(_trail[i])

func advance(delta: float, bus_phase: String, boarding_point: Vector3, dialogue_open: bool) -> void:
	if not is_finite(delta): return
	if state == "boarded":
		if bus_phase == "departing": departed = true
		return
	var dt := maxf(delta, 0.0)
	_advance_thanks(dt)
	_time += dt
	if state == "wait":
		visual.position.y = sin(_time * 1.7) * 0.008
		visual.rotation.y = sin(_time * 0.32) * 0.09
		if bus_phase != "stopped":
			_stop_time = 0.0
			return
		_stop_time += dt
		var delay := dialogue_departure_delay if dialogue_open else door_open_delay
		if _stop_time < delay:
			return
		# Only time after the delay can be spent moving this update.
		dt = minf(dt, _stop_time - delay)
		_start_walk(boarding_point)
	if bus_phase != "stopped" and not returning:
		_return_home()
	var budget := dt * walk_speed
	while not _path.is_empty():
		var target := _path[0]
		var difference := target - global_position
		var distance := difference.length()
		if distance > 0.001:
			visual.rotation.y = lerp_angle(visual.rotation.y, atan2(difference.x, difference.z), minf(dt * 8.0, 1.0))
		if distance > budget:
			global_position += difference.normalized() * budget
			break
		global_position = target
		budget -= distance
		_path.pop_front()
		if not returning:
			_trail.append(target)
	visual.position.y = absf(sin(_time * 7.0)) * 0.025
	visual.get_node("LegLeft").rotation.x = sin(_time * 7.0) * 0.12
	visual.get_node("LegRight").rotation.x = -sin(_time * 7.0) * 0.12
	if _path.is_empty():
		if returning:
			reset()
		else:
			leave_with_player()

func request_thanks() -> bool:
	if not is_available() or thanking: return false
	thanking = true
	thanks_elapsed = 0.0
	return true

func _advance_thanks(delta: float) -> void:
	if not thanking: return
	thanks_elapsed = minf(thanks_elapsed+delta,maxf(thanks_duration,0.01))
	head_pivot.transform = _head_rest
	head_pivot.rotate_object_local(Vector3.RIGHT,sin(PI*thanks_elapsed/maxf(thanks_duration,0.01))*clampf(thanks_angle,0.0,0.4))
	if thanks_elapsed >= maxf(thanks_duration,0.01): _cancel_thanks()

func _cancel_thanks() -> void:
	thanking = false
	thanks_elapsed = 0.0
	head_pivot.transform = _head_rest
