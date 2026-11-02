extends Node3D
## Optional original instrumental radio. No speech and no global audio mutation.
@export_range(-60.0, -6.0, 0.5) var listening_volume_db := -23.0
@onready var player: AudioStreamPlayer3D = $Player
var is_on := false
var muted := false

func _ready() -> void:
	# Import settings remain portable. Duplicate before configuring the loop so
	# two scene instances never mutate a shared imported stream.
	var loop := player.stream.duplicate() as AudioStreamWAV
	loop.loop_mode = AudioStreamWAV.LOOP_FORWARD
	loop.loop_begin = 0
	loop.loop_end = int(loop.get_length() * loop.mix_rate)
	player.stream = loop
	reset()

func toggle() -> void:
	is_on = not is_on
	if is_on:
		player.play()
	else:
		player.stop()

func reset() -> void:
	is_on = false
	muted = false
	player.stop()
	player.volume_db = listening_volume_db

func set_muted(value: bool) -> void:
	muted = value
	player.volume_db = -80.0 if muted else listening_volume_db

func caption() -> String:
	return "작은 라디오 · 느린 건반 선율" if is_on else "작은 라디오 · 꺼져 있음"

func _exit_tree() -> void:
	if is_instance_valid(player):
		player.stop()
