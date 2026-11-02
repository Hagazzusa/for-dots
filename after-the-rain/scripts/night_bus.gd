extends Node3D
## Owns only route state. Composition root explicitly advances this controller.
## Dependency: its saved Visual child implements set_door_open(bool) and set_route_opacity(float).
const Schedule = preload("res://config/bus_schedule.gd")
signal arrived
signal phase_changed(new_phase: String)

@export var schedule: Schedule = preload("res://config/bus_schedule.tres")
var phase := "waiting"
var phase_time := 0.0
var paused := false
@onready var visual: Node3D = get_node_or_null("Visual")

func _ready() -> void:
	position.x = schedule.approach_x
	position.z = schedule.lane_z
	_update_visual()

func advance(delta: float) -> void:
	if paused:
		return
	# Intentionally preserve v3: at most one transition per call; discard excess delta.
	phase_time += delta
	match phase:
		"waiting":
			position.x = schedule.approach_x
			if phase_time >= schedule.wait_seconds:
				_transition("approaching")
		"approaching":
			var t := minf(phase_time / schedule.approach_seconds, 1.0)
			position.x = lerpf(schedule.approach_x, schedule.stop_x, 1.0-pow(1.0-t, 2))
			if phase_time >= schedule.approach_seconds:
				position.x = schedule.stop_x
				_transition("stopped")
				_set_doors(true)
				arrived.emit()
		"stopped":
			if phase_time >= schedule.stop_seconds:
				_transition("departing")
				_set_doors(false)
		"departing":
			var t := minf(phase_time / schedule.departure_seconds, 1.0)
			position.x = lerpf(schedule.stop_x, schedule.departure_x, pow(t, 2))
			if phase_time >= schedule.departure_seconds:
				_transition("waiting")

	_update_visual()

func _update_visual() -> void:
	# Only distant endpoints fade; session alone owns this controller root visibility.
	var opacity := 1.0
	match phase:
		"waiting": opacity = 0.0
		"approaching": opacity = smoothstep(0.0, 12.0, absf(position.x - schedule.approach_x))
		"departing": opacity = smoothstep(0.0, 12.0, absf(schedule.departure_x - position.x))
	if is_instance_valid(visual) and visual.has_method("set_route_opacity"):
		visual.set_route_opacity(opacity)

func _transition(next_phase: String) -> void:
	phase = next_phase
	phase_time = 0.0
	_update_visual()
	phase_changed.emit(phase)

func _set_doors(open: bool) -> void:
	if is_instance_valid(visual) and visual.has_method("set_door_open"):
		visual.set_door_open(open)

func set_paused(value: bool) -> void:
	paused = value

func close_doors() -> void:
	_set_doors(false)

func reset() -> void:
	var changed := phase != "waiting"
	phase = "waiting"
	phase_time = 0.0
	paused = false
	position.x = schedule.approach_x
	position.z = schedule.lane_z
	_update_visual()
	close_doors()
	if changed:
		phase_changed.emit(phase)

func countdown_seconds() -> int:
	return maxi(0, ceili(schedule.wait_seconds-phase_time+schedule.approach_seconds))

func status_text() -> String:
	match phase:
		"waiting": return "08  HOME  /  %02ds" % countdown_seconds()
		"approaching": return "08  HOME  /  arriving"
		"stopped": return "08  HOME  /  doors open"
		"departing": return "08  HOME  /  see you soon"
	return "08  HOME"
