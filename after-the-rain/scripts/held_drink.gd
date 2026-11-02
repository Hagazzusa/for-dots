extends Node3D
## Presentation-only attachment: scene-local cup and steam, no game-state ownership.
@export var resting_position := Vector3(.28,-.32,-.6)
@export var sipping_position := Vector3(.08,-.12,-.36)
@export var pose_speed := 6.0
@export var resting_tilt := .28
@export var sip_tilt := .38
@export var sip_duration := 1.3
@export var movement_impulse_scale := .4
var previous_walk := Vector2.ZERO
@onready var cup: Node3D = $Cup
@onready var steam: Array = $Steam.get_children()

func _ready():
	position = resting_position
	hide()

func set_fill(amount: float, immediate := false):
	cup.set_fill(amount,immediate)

func impulse(force: Vector2):
	cup.impulse(force)

func reset_visuals():
	previous_walk = Vector2.ZERO
	cup.set_fill(0,true)
	hide()

func present(sips: int, has_cup: bool, sip_time: float, boarded: bool, player_velocity: Vector3, player_yaw: float, seated: bool, delta: float, elapsed_time: float):
	var angle := resting_tilt + (sip_tilt*sin((1.0-sip_time/sip_duration)*PI) if sip_time>0 else 0.0)
	global_rotation = Vector3(angle,player_yaw,0)
	var local_walk := Basis(Vector3.UP,player_yaw).inverse()*player_velocity
	var walk := Vector2(local_walk.x,local_walk.z) if not seated else Vector2.ZERO
	cup.impulse((walk-previous_walk)*movement_impulse_scale)
	previous_walk = walk
	cup.update_liquid(delta,cup.global_basis.inverse()*Vector3.UP)
	position = position.lerp(sipping_position if sip_time>0 else resting_position,minf(delta*pose_speed,1))
	visible = has_cup and not boarded
	for i in range(steam.size()):
		var t := fmod(elapsed_time*.35+i*.08,.4)
		steam[i].position = Vector3(sin(t*15+i)*.018,.07+t,0)
		steam[i].visible = sips>0
