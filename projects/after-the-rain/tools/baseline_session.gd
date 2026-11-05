extends Node3D
## Composition root: commands/signals and session flow, not geometry or subsystem state.
@export var seat_radius := 2.6
@export var boarding_radius := 1.7
@export var vending_radius := 1.8
@onready var world = $World
@onready var player = $Player
@onready var bus = $NightBus
@onready var drink = $DrinkSession
@onready var rain = $Rain
@onready var ambience = $Ambience
@onready var hud = $HUD
var boarded := false
var photo_mode := false
var time := 0.0
var warmth := 0.0
var note := "Just one more stop, then home."
var note_time := 7.0
var testing := false

func _ready():
	testing = "--test" in OS.get_cmdline_user_args()
	# All child _ready callbacks are self-contained; wire only after they exist.
	player.interaction_requested.connect(interact)
	player.action_requested.connect(drink_action)
	player.restart_requested.connect(restart)
	player.photo_requested.connect(photo_view)
	player.mute_requested.connect(ambience.toggle_mute)
	player.capture_requested.connect(capture_preview)
	player.look_impulse.connect(_on_look)
	drink.dispense_started.connect(ambience.play_chime)
	drink.sip_started.connect(_on_sip)
	drink.fill_target_changed.connect(player.held_drink.set_fill)
	drink.note_requested.connect(set_note)
	bus.arrived.connect(ambience.play_chime)
	var positions:Array=[]
	for p in JSON.parse_string(FileAccess.get_file_as_string("res://config/rain_positions.json")):
		positions.append(Vector3(p[0],p[1],p[2]))
	rain.initialize(positions)
	player.reset(world.anchor("Start"))
	ambience.start()
	if testing:
		player.input_enabled=false
		call_deferred("run_tests")
	else:
		Input.mouse_mode=Input.MOUSE_MODE_CAPTURED

func _on_look(force:Vector2):
	if drink.has_cup:
		player.held_drink.impulse(force)
func _on_sip():
	warmth=45
	player.held_drink.impulse(Vector2(.2,.9))
func set_note(text:String,duration:float):
	note=text
	note_time=duration
func near(id:String,distance:float)->bool:
	return player.position.distance_to(world.anchor(id))<distance

func interact():
	if boarded:
		return
	photo_mode=false
	player.set_motion_enabled(true)
	if player.seated:
		player.stand(world.anchor("Stand"))
	elif bus.phase=="stopped" and near("Boarding",boarding_radius):
		board_bus()
	elif near("Seat",seat_radius):
		player.sit(world.anchor("Seat"))
func drink_action():
	drink.request_action(near("Vending",vending_radius) and not player.seated,boarded)
func board_bus():
	if boarded or player.seated or bus.phase!="stopped":
		return
	boarded=true
	bus.set_paused(true)
	bus.close_doors()
	player.set_motion_enabled(false)
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
func restart():
	boarded=false
	photo_mode=false
	player.reset(world.anchor("Start"))
	drink.reset()
	player.held_drink.reset_visuals()
	bus.reset()
	warmth=0
	set_note("Just one more stop, then home.",7)
	if not testing:
		Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
func photo_view():
	if boarded:return
	photo_mode=true
	player.set_photo_view(Vector3(5.5,2.7,10),Vector3(0,1.2,0))

func hint_text()->String:
	if boarded:return ""
	if player.seated:
		return "[E] Stand up"+("     [F] Sip warm cocoa" if drink.sips>0 else "     Stay a while. There's no hurry.")
	if bus.phase=="stopped" and near("Boarding",boarding_radius):
		return "[E] Board the 08 home     /     Or let this one pass."
	if near("Vending",vending_radius):
		return "Preparing your cocoa..." if drink.dispensing>0 else ("[F] Sip warm cocoa" if drink.sips>0 else "[F] Get a hot cocoa  /  on the house tonight")
	if near("Seat",seat_radius):
		return "[E] Sit and listen"+("     [F] Sip cocoa" if drink.sips>0 else "")
	return "[F] Sip warm cocoa" if drink.sips>0 else "A warm drink might be nice. The machine is still on."

func _process(delta):
	time+=delta
	var hint=hint_text()
	if not testing:
		bus.advance(delta)
	drink.advance(delta)
	player.held_drink.present(drink.sips,drink.has_cup,drink.sip_time,boarded,player.velocity,player.rotation.y,player.seated,delta,time)
	warmth=maxf(0,warmth-delta)
	note_time=maxf(0,note_time-delta)
	var sheltered=world.is_sheltered(player.position)
	ambience.advance(delta,sheltered,boarded,bus.phase)
	var feeling="" if boarded else (note if note_time>0 else ("The rain is softer beneath the roof." if sheltered else ("The cocoa's warmth lingers." if warmth>0 else "Cool rain on your sleeves. The shelter is close.")))
	hud.present(hint,feeling,bus.status_text(),boarded)
	rain.advance(delta)

func capture_preview():
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://preview.png")
	print("Preview saved")
func run_tests():
	var runner=load("res://tests/regression.gd").new()
	add_child(runner)
	await runner.run(self)
	ambience.stop_all()
	for audio in ambience.get_children():
		if audio is AudioStreamPlayer:audio.stream=null
	await get_tree().create_timer(.5).timeout
	get_tree().quit()
