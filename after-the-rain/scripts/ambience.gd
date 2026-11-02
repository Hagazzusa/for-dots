extends Node
## One active ambience mix per game. The named project bus/filter is intentionally
## global; simultaneous instances share that mix, but never allocate extra buses.
@export var outside_cutoff_hz := 12000.0
@export var shelter_cutoff_hz := 1700.0
@export var outside_rain_db := -11.0
@export var sheltered_rain_db := -18.0
@export var boarded_rain_db := -23.0
@export var smoothing_speed := 2.0
@export var umbrella_cutoff_hz := 4200.0
@export var umbrella_rain_db := -14.0
@export var canopy_taps_db := -27.0
@export var footstep_interval := .45
@onready var canopy_player: AudioStreamPlayer = $CanopyPlayer
@onready var wet_footsteps: AudioStreamPlayer = $WetFootsteps
@onready var roof_footsteps: AudioStreamPlayer = $RoofFootsteps
var _step_time := 0.0
@onready var rain_player: AudioStreamPlayer = $RainPlayer
@onready var engine_player: AudioStreamPlayer = $EnginePlayer
@onready var chime_player: AudioStreamPlayer = $ChimePlayer
var rain_filter: AudioEffectLowPassFilter

func _ready() -> void:
	# One private loop configuration per instance; no shared stream mutation.
	var loop = canopy_player.stream.duplicate() as AudioStreamWAV
	loop.loop_mode = AudioStreamWAV.LOOP_FORWARD
	loop.loop_begin = 0
	loop.loop_end = int(loop.get_length()*loop.mix_rate)
	canopy_player.stream = loop
	var index := AudioServer.get_bus_index("ShelterRain")
	if index >= 0 and AudioServer.get_bus_effect_count(index) > 0:
		rain_filter = AudioServer.get_bus_effect(index,0) as AudioEffectLowPassFilter
	else:
		push_warning("Ambience expects the project's default_bus_layout.tres (ShelterRain). No runtime buses were created.")

func start() -> void:
	rain_player.play()
	engine_player.play()
	canopy_player.play()

func advance(delta: float, sheltered: bool, boarded: bool, bus_phase: String, umbrella_open: bool = false) -> void:
	var weight := clampf(delta*smoothing_speed,0.0,1.0)
	var canopy_active := umbrella_open and not sheltered and not boarded
	var cutoff := shelter_cutoff_hz if sheltered or boarded else (umbrella_cutoff_hz if canopy_active else outside_cutoff_hz)
	var rain_target := boarded_rain_db if boarded else (sheltered_rain_db if sheltered else (umbrella_rain_db if canopy_active else outside_rain_db))
	if rain_filter:
		rain_filter.cutoff_hz = lerpf(rain_filter.cutoff_hz,cutoff,weight)
	rain_player.volume_db = lerpf(rain_player.volume_db,rain_target,weight)
	canopy_player.volume_db = lerpf(canopy_player.volume_db,canopy_taps_db if canopy_active else -80.0,weight)
	var engine_target := -25.0 if bus_phase == "stopped" else (-29.0 if bus_phase in ["approaching","departing"] else -65.0)
	engine_player.volume_db = lerpf(engine_player.volume_db,engine_target,weight)

## Session calls this only for actual walking; no automatic process/input dependency.
func footsteps(delta: float, moving: bool, sheltered: bool) -> void:
	_step_time = maxf(0.0,_step_time-maxf(delta,0.0))
	if not moving or _step_time > 0.0:
		return
	(roof_footsteps if sheltered else wet_footsteps).play()
	_step_time = maxf(.1,footstep_interval)

## Restart mix/timers without changing Master mute or allocating new players/buses.
func reset() -> void:
	_step_time = 0.0
	wet_footsteps.stop()
	roof_footsteps.stop()
	chime_player.stop()
	rain_player.volume_db = outside_rain_db
	engine_player.volume_db = -40.0
	canopy_player.volume_db = -80.0
	if rain_filter:
		rain_filter.cutoff_hz = outside_cutoff_hz

func play_chime() -> void:
	chime_player.play()

func toggle_mute() -> void:
	AudioServer.set_bus_mute(0,not AudioServer.is_bus_mute(0))

func stop_all() -> void:
	rain_player.stop()
	engine_player.stop()
	chime_player.stop()
	canopy_player.stop()
	wet_footsteps.stop()
	roof_footsteps.stop()
	_step_time = 0.0

func _exit_tree() -> void:
	stop_all()
