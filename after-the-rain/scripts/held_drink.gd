extends Node3D
## Presentation only: DrinkSession supplies heat and normalized sip phase.
## Reconstructed steam/grip; approved liquid mesh and slosh remain untouched.
@export var resting_position := Vector3(.28,-.32,-.6)
@export var sipping_position := Vector3(.08,-.12,-.36)
@export var pose_speed := 6.0
@export var resting_tilt := .28
@export var sip_tilt := .38
@export var movement_impulse_scale := .4
@export var seated_height_floor := -.43
var previous_walk := Vector2.ZERO
var _heat := 0.0
var _sheltered := false
var _covered := false
@onready var cup: Node3D = $Cup
@onready var steam: Node3D = $Steam
func _ready():
	position = resting_position
	hide()
func set_fill(amount: float, immediate := false):
	cup.set_fill(amount,immediate)
	if immediate or amount <= 0: steam.reset()
func impulse(force: Vector2):
	cup.impulse(force)
func set_warmth_context(heat: float, sheltered: bool, covered: bool) -> void:
	_heat = clampf(heat, 0, 1)
	_sheltered = sheltered
	_covered = covered
func reset_visuals():
	previous_walk = Vector2.ZERO
	_heat = 0
	_sheltered = false
	_covered = false
	position = resting_position
	cup.set_fill(0,true)
	steam.reset()
	hide()
## sip_progress=-1 inactive; 0..1 is active. No duration/countdown is owned here.
## elapsed_time retained for call-shape compatibility, deliberately not used as a clock.
func present(sips: int, has_cup: bool, sip_progress: float, blocked: bool, player_velocity: Vector3, player_yaw: float, seated: bool, delta: float, _elapsed_time: float = 0.0):
	var sipping := sip_progress >= 0.0
	var progress := clampf(sip_progress, 0, 1)
	var angle := resting_tilt + (sip_tilt * sin(progress * PI) if sipping else 0.0)
	global_rotation = Vector3(angle,player_yaw,0)
	var local_walk := Basis(Vector3.UP,player_yaw).inverse()*player_velocity
	var walk := Vector2(local_walk.x,local_walk.z) if not seated else Vector2.ZERO
	cup.impulse((walk-previous_walk)*movement_impulse_scale)
	previous_walk = walk
	cup.update_liquid(delta,cup.global_basis.inverse()*Vector3.UP)
	position = position.lerp(sipping_position if sipping else resting_position,clampf(delta*pose_speed,0,1))
	if seated and get_parent() is Node3D:
		# Camera pitch rotates attachment translation: clamp in WORLD Y, not local Y.
		global_position.y = maxf(global_position.y, (get_parent() as Node3D).global_position.y + seated_height_floor)
	visible = has_cup and not blocked
	steam.advance(delta, cup.to_global(Vector3(0,.09,0)), visible and sips>0 and not sipping, _heat, _sheltered, _covered)
