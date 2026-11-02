extends Node3D
## Composition root: commands/signals and session flow, not geometry or subsystem state.
@export var seat_radius := 2.6
@export var boarding_radius := 1.7
@export var vending_radius := 1.8
@export var disposal_radius := 1.6
@onready var clock = $EveningClock
@onready var exchange = $UmbrellaExchange
@onready var pause_overlay = $PauseOverlay
@onready var exploration = get_node_or_null("Exploration")
@onready var umbrella = $Player/Camera3D/HeldUmbrella
@onready var story = get_node_or_null("StoryCorner")
@onready var world = $World
@onready var player = $Player
@onready var bus = $NightBus
@onready var drink = $DrinkSession
@onready var rain = $Rain
@onready var ambience = $Ambience
@onready var hud = $HUD
@onready var onboard = $OnboardView
@onready var arrival_display = $World/BusStop/ArrivalDisplay
@onready var disposal_point = $World/BusStop/TrashCan/Interaction
var ride_finished := false
var boarded := false
var photo_mode := false
var time := 0.0
var warmth := 0.0
var note := "Just one more stop, then home."
var note_time := 7.0
var testing := false
var ride_note := ""

func _ready():
	testing = "--test" in OS.get_cmdline_user_args() and ResourceLoader.exists("res://tests/regression.gd")
	pause_overlay.restart_requested.connect(restart)
	pause_overlay.mute_requested.connect(ambience.toggle_mute)
	# All child _ready callbacks are self-contained; wire only after they exist.
	if exploration:
		exploration.initialize(umbrella,story.panel)
		exploration.shared_available=func():return not exchange.loaned
	exchange.initialize(umbrella,story.objects.get_node("Passenger"),story.panel)
	player.quiet_wait_requested.connect(wait_quietly)
	player.loan_requested.connect(offer_umbrella)
	player.umbrella_requested.connect(toggle_umbrella)
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
	onboard.finished.connect(_on_ride_finished)
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

func can_offer_umbrella()->bool:
	return not boarded and not photo_mode and not story.panel.is_open and exchange.can_offer() and story.target(player.camera,player.global_position)=="Passenger"
func offer_umbrella():
	if can_offer_umbrella():exchange.request_offer()
func wait_quietly():
	if boarded or photo_mode or not player.seated:return
	var skipped:float=bus.skip_waiting()
	if skipped<0:return
	clock.advance(skipped)
	set_note("잠깐 눈을 감았다. 멀리서 버스 불빛이 다가온다.",5)
func toggle_umbrella():
	if not boarded: umbrella.toggle_open()

func _on_look(force:Vector2):
	if drink.has_cup:
		player.held_drink.impulse(force)
func _on_sip():
	warmth=45
	player.held_drink.impulse(Vector2(.2,.9))
func set_note(text:String,duration:float):
	note=text
	note_time=duration
func _on_ride_finished():
	ride_finished=true
func near_disposal()->bool:
	return player.global_position.distance_to(disposal_point.global_position)<disposal_radius
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
	elif near_disposal() and drink.has_cup and drink.sips==0:
		if drink.dispose_empty():
			player.held_drink.reset_visuals()
	elif story and story.panel.is_open:
		story.panel.advance()
	elif exploration and exploration.try_interact(player.camera,player.global_position):
		pass
	elif story and story.try_interact(player.camera,player.global_position):
		pass
	elif near("Seat",seat_radius):
		player.sit(world.anchor("Seat"))
func drink_action():
	drink.request_action(near("Vending",vending_radius) and not player.seated,boarded)
func board_bus():
	if boarded or player.seated or bus.phase!="stopped":
		return
	var passenger=story.objects.get_node("Passenger")
	ride_note=exchange.boarding_caption(passenger.state=="boarded" and not exchange.departed)
	if story:
		story.leave()
		story.objects.get_node("Passenger").leave_with_player()
		exchange.present(0,bus.phase)
	umbrella.hide()
	boarded=true
	bus.set_paused(true)
	bus.close_doors()
	bus.hide()
	onboard.begin()
	ride_finished=false
	player.set_motion_enabled(false)
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
func restart():
	pause_overlay.reset()
	exchange.reset()
	clock.reset()
	ride_note=""
	ambience.reset()
	if story: story.reset()
	if exploration: exploration.reset()
	umbrella.reset()
	boarded=false
	ride_finished=false
	onboard.reset()
	player.camera.make_current()
	bus.show()
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
	if boarded:return "[R] Start another rainy evening" if ride_finished else "A window seat. The city slips quietly by."
	if player.seated:
		return "[E] Stand up"+("     [F] Sip warm cocoa" if drink.sips>0 else "     Stay a while. There's no hurry.")+("    [T] 조용히 기다리기" if bus.phase=="waiting" else "")
	if bus.phase=="stopped" and near("Boarding",boarding_radius):
		return "[E] Board the 08 home     /     Or let this one pass."
	if near_disposal() and drink.has_cup and drink.sips==0:
		return "[E] Put the empty cup in the bin"
	if exploration and not story.panel.is_open:
		var exploration_hint=exploration.hint(player.camera,player.global_position)
		if not exploration_hint.is_empty(): return exploration_hint
	if can_offer_umbrella():return "[E] 승객과 이야기하기    [G] 우산 빌려주기 이야기"
	if story:
		var story_hint=story.hint(player.camera,player.global_position)
		if not story_hint.is_empty(): return story_hint
	if near("Vending",vending_radius):
		return "Preparing your cocoa..." if drink.dispensing>0 else ("[F] Sip warm cocoa" if drink.sips>0 else "[F] Get a hot cocoa  /  on the house tonight")
	if near("Seat",seat_radius):
		return "[E] Sit and listen"+("     [F] Sip cocoa" if drink.sips>0 else "")
	return "[F] Sip warm cocoa" if drink.sips>0 else "A warm drink might be nice. The machine is still on."

func _process(delta):
	time+=delta
	if not ride_finished:clock.advance(delta)
	hud.set_clock(clock.time_text())
	var hint=hint_text()
	if not testing:
		bus.advance(delta)
	if story and not boarded:
		story.advance_passenger(delta,bus.phase,world.anchor("Boarding")+Vector3(0,0,.65))
		story.objects.get_node("SharedUmbrella").visible=not umbrella.held and not exchange.loaned
	if not boarded:exchange.present(delta,bus.phase)
	umbrella.present(delta,player.velocity)
	drink.advance(delta)
	onboard.advance(delta)
	arrival_display.present("departing" if boarded else bus.phase,bus.countdown_seconds())
	player.held_drink.present(drink.sips,drink.has_cup,drink.sip_time,boarded,player.velocity,player.rotation.y,player.seated,delta,time)
	warmth=maxf(0,warmth-delta)
	note_time=maxf(0,note_time-delta)
	var sheltered=world.is_sheltered(player.position)
	var covered=umbrella.held and umbrella.is_open and not boarded
	rain.set_umbrella_cover(player.global_position,covered)
	ambience.advance(delta,sheltered,boarded,bus.phase,covered)
	ambience.footsteps(delta,Vector2(player.velocity.x,player.velocity.z).length()>0.2 and player.motion_enabled and not player.seated and not boarded,sheltered)
	var feeling=ride_note if boarded else (note if note_time>0 else ("The rain is softer beneath the roof." if sheltered else ("The cocoa's warmth lingers." if warmth>0 else "Cool rain on your sleeves. The shelter is close.")))
	if story and not boarded and not story.caption(player.global_position).is_empty():
		feeling=story.caption(player.global_position)
	if umbrella.held and not boarded:
		hint+="   [U] 우산 접기" if umbrella.is_open else "   [U] 우산 펴기"
	if covered and not sheltered: feeling="우산 위로 빗방울이 톡톡 떨어진다. 꽃집 불빛은 왼쪽 골목에 있다."
	hud.present(hint,feeling,"" if boarded else bus.status_text(),ride_finished)
	hud.set_riding(boarded)
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
