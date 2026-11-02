extends CharacterBody3D
## Owns locomotion and view. Emits intents; never queries sibling gameplay nodes.
signal quiet_wait_requested
signal loan_requested
signal umbrella_requested
signal interaction_requested
signal action_requested
signal restart_requested
signal photo_requested
signal mute_requested
signal capture_requested
signal look_impulse(force: Vector2)

@export var move_speed := 2.4
@export var mouse_sensitivity := .002
@export var keyboard_look_speed := 1.0
@export var safe_x_bounds := Vector2(-12,12)
@export var safe_z_bounds := Vector2(-8,2.65)
@export var input_enabled := true
var seated := false
var motion_enabled := true
@onready var camera: Camera3D = $Camera3D
@onready var held_drink: Node3D = $Camera3D/HeldDrink

func _unhandled_input(event: InputEvent):
	if not input_enabled:
		return
	if motion_enabled and event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		if event.relative.length() < 150:
			look_impulse.emit(Vector2(-event.relative.x,event.relative.y)*.02)
			rotation.y -= event.relative.x*mouse_sensitivity
			camera.rotation.x = clampf(camera.rotation.x-event.relative.y*mouse_sensitivity,-1.15,1.15)
	if event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ESCAPE: Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
			KEY_T: quiet_wait_requested.emit()
			KEY_G: loan_requested.emit()
			KEY_U: umbrella_requested.emit()
			KEY_E: interaction_requested.emit()
			KEY_F: action_requested.emit()
			KEY_R: restart_requested.emit()
			KEY_P: photo_requested.emit()
			KEY_M: mute_requested.emit()
			KEY_F12: capture_requested.emit()

func apply_keyboard_look(axis: Vector2, delta: float) -> void:
	if not input_enabled or not motion_enabled:
		return
	var step := axis.limit_length(1.0) * keyboard_look_speed * clampf(delta,0.0,.1)
	rotation.y -= step.x
	camera.rotation.x = clampf(camera.rotation.x + step.y,-1.15,1.15)
	if not step.is_zero_approx():
		look_impulse.emit(Vector2(-step.x,-step.y)*10.0)

func _physics_process(_delta: float):
	var look_axis := Vector2(float(Input.is_key_pressed(KEY_RIGHT))-float(Input.is_key_pressed(KEY_LEFT)),float(Input.is_key_pressed(KEY_UP))-float(Input.is_key_pressed(KEY_DOWN)))
	apply_keyboard_look(look_axis,_delta)
	if not motion_enabled or seated:
		return
	var direction := Vector3(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),0,float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W))) if input_enabled else Vector3.ZERO
	var movement := basis*direction.normalized()*move_speed
	if position.z < 2.5 and position.z > 1.95 and movement.z < 0 and is_on_floor():
		position.y = maxf(position.y,1.64)
	velocity = Vector3(movement.x,-1.0,movement.z)
	move_and_slide()
	position.x = clampf(position.x,safe_x_bounds.x,safe_x_bounds.y)
	position.z = clampf(position.z,safe_z_bounds.x,safe_z_bounds.y)

func sit(seat_position: Vector3):
	seated = true
	position = seat_position
	rotation.y = PI
	camera.rotation = Vector3(-.04,0,0)

func stand(stand_position: Vector3):
	seated = false
	position = stand_position

func reset(start_position: Vector3):
	seated = false
	motion_enabled = true
	position = start_position
	rotation = Vector3(0,-.85,0)
	camera.rotation = Vector3.ZERO
	velocity = Vector3.ZERO

func set_motion_enabled(enabled: bool):
	motion_enabled = enabled

func set_photo_view(view_position: Vector3, target: Vector3):
	seated = false
	motion_enabled = false
	position = view_position
	rotation.y = 0
	camera.look_at(target)
