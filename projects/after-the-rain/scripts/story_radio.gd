extends Node3D
## Original 48-second instrumental: three 16-second phrases.
## Captions read the audio player, never the evening/world clock. No speech.
@export_range(-60.0, -6.0, 0.5) var listening_volume_db := -23.0
@onready var player: AudioStreamPlayer3D = $Player
signal power_changed(powered: bool)
var shutting_down := false
const AudioRelease = preload("res://scripts/audio_release.gd")
var is_on := false
var muted := false
const PHRASE_SECONDS := 16.0
const LOOP_SECONDS := 48.0
const PHRASE_CAPTIONS: Array[String] = [
	"작은 라디오 · 빗방울 사이로 느린 건반 선율",
	"작은 라디오 · 낮은 화음 위로 맑은 음이 번집니다",
	"작은 라디오 · 마지막 음이 천천히 제자리로 돌아옵니다",
]

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
	if shutting_down:return
	is_on = not is_on
	if is_on:
		player.play()
	else:
		player.stop()
	power_changed.emit(is_on)

func reset() -> void:
	if shutting_down:return
	is_on = false
	muted = false
	player.stop()
	player.volume_db = listening_volume_db
	power_changed.emit(false)

func set_muted(value: bool) -> void:
	muted = value
	player.volume_db = -80.0 if muted else listening_volume_db

func playback_seconds() -> float:
	return maxf(0.0, player.get_playback_position()) if is_on else 0.0

func caption_for_position(seconds: float) -> String:
	var wrapped := fposmod(maxf(0.0, seconds), LOOP_SECONDS)
	var index := mini(2, int(wrapped / PHRASE_SECONDS))
	return PHRASE_CAPTIONS[index]

func caption() -> String:
	return caption_for_position(playback_seconds()) if is_on else "작은 라디오 · 꺼져 있음"

func _exit_tree() -> void:
	if is_instance_valid(player):
		player.stop()


func begin_shutdown() -> Array[WeakRef]:
	if shutting_down:return []
	shutting_down=true
	is_on=false
	power_changed.emit(false)
	return AudioRelease.stop_player(player)
