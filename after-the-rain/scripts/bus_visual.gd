extends Node3D
## Authored two-leaf telescoping door. Recess first, then slide behind the entry.
## Reverse order on close avoids the front axle and keeps panels inside the bus.
@export var door_duration := .7
@onready var doors: Array[Node3D] = [$Doors/Left, $Doors/Right]
var door_tween: Tween
var door_open := false
const CLOSED_X := [2.475, 3.125]
const OPEN_X := [1.8, 1.8]
const CLOSED_Z := -1.18
const POCKET_Z := [-.70, -.50]

func set_door_open(value: bool):
	door_open = value
	if door_tween:
		door_tween.kill()
	door_tween = create_tween()
	# Parallel pairs are separated by a sequential phase boundary.
	for i in range(doors.size()):
		var property := "position:z" if value else "position:x"
		var target: float = POCKET_Z[i] if value else CLOSED_X[i]
		door_tween.tween_property(doors[i], property, target, door_duration * .35).set_trans(Tween.TRANS_SINE)
		if i == 0:
			door_tween.parallel()
	for i in range(doors.size()):
		var property := "position:x" if value else "position:z"
		var target: float = OPEN_X[i] if value else CLOSED_Z
		door_tween.tween_property(doors[i], property, target, door_duration * .65).set_trans(Tween.TRANS_SINE)
		if i == 0:
			door_tween.parallel()
