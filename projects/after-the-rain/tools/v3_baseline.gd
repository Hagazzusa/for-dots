extends Node3D

var player: CharacterBody3D
var camera: Camera3D
var hint: Label
var sound: AudioStreamPlayer
var seated := false
var muted := false
var time := 0.0
var rain: MultiMeshInstance3D
var drops: Array[Vector3] = []
var rng := RandomNumberGenerator.new()
var seat := Vector3(-1.0, 1.25, -0.12)
var screenshot_mode := false
var photo_mode := false
var bus: Node3D
var bus_phase := "waiting"
var phase_time := 0.0
var bus_status: Label
var feeling: Label
var ending: Control
var boarded := false
var cup: Node3D
var steam: Array[MeshInstance3D] = []
var sips := 0
var has_cup := false
var fill_pending := false
var previous_walk := Vector2.ZERO
var dispensing := 0.0
var sip_time := 0.0
var warmth := 0.0
var note := "Just one more stop, then home."
var note_time := 7.0
var rain_filter: AudioEffectLowPassFilter
var chime: AudioStreamPlayer
var engine: AudioStreamPlayer
var testing := false
const START := Vector3(-4.6,1.65,2.4)
const DOOR := Vector3(2.4,1.5,2.65)
const VENDING := Vector3(2.2,1.5,.75)

func material(color: Color, rough := 0.8, glow := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	if glow > 0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = glow
	return m

func box(pos: Vector3, size: Vector3, mat: Material, solid := false) -> MeshInstance3D:
	var n := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	n.mesh = mesh
	n.material_override = mat
	add_child(n)
	n.position = pos
	if solid:
		collider(pos, size)
	return n

func collider(pos: Vector3, size: Vector3):
	var body := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	col.shape = shape
	body.add_child(col)
	add_child(body)
	body.position = pos

func light(pos: Vector3, color: Color, energy: float, radius: float):
	var l := OmniLight3D.new()
	l.light_color = color
	l.light_energy = energy
	l.omni_range = radius
	l.omni_attenuation = 1.35
	add_child(l)
	l.position = pos

func lettering(text: String, pos: Vector3, size: int, color: Color) -> Label3D:
	var l := Label3D.new()
	l.text = text
	l.font_size = size
	l.pixel_size = .005
	l.modulate = color
	l.no_depth_test = false
	l.outline_size = 0
	add_child(l)
	l.position = pos
	return l

func _ready():
	rng.seed = 73
	testing = "--test" in OS.get_cmdline_user_args()
	screenshot_mode = "--preview" in OS.get_cmdline_user_args()
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color("101d2d")
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color("607d9a")
	e.ambient_light_energy = .48
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	e.fog_enabled = true
	e.fog_light_color = Color("192b3a")
	e.fog_density = .022
	env.environment = e
	add_child(env)
	var moon := DirectionalLight3D.new()
	moon.light_color = Color("7c9dbd")
	moon.light_energy = .4
	moon.rotation_degrees = Vector3(-48,-25,0)
	add_child(moon)
	var asphalt := material(Color("17232c"),.16)
	asphalt.metallic = .65
	box(Vector3(0,-.2,4),Vector3(70,.3,60),asphalt,true)
	box(Vector3(0,-.02,-.5),Vector3(18,.24,5),material(Color("45545b"),.38),true)
	box(Vector3(0,.12,2.05),Vector3(18,.15,.22),material(Color("b2b1a0"),.5))
	for x in range(-8,9):
		box(Vector3(x,.106,-.5),Vector3(.018,.01,5),material(Color("303d43")))
	for x in range(-24,25,4):
		box(Vector3(x,-.039,6),Vector3(2.0,.012,.1),material(Color("b6aa7c"),.5))
	if ResourceLoader.exists("res://assets/shelter.glb"):
		add_child(load("res://assets/shelter.glb").instantiate())
	collider(Vector3(0,1.4,-1.2),Vector3(7,2.8,.15))
	collider(Vector3(-1,.6,-.45),Vector3(3.2,1.05,.6))
	collider(Vector3(2.2,1,-.2),Vector3(1.25,2,.85))
	for x in [-3.2,3.2]:
		for z in [-1.0,1.0]:
			collider(Vector3(x,1.5,z),Vector3(.17,3,.17))
	var warm := Color("ffca7a")
	box(Vector3(-.5,2.78,.1),Vector3(3.7,.035,.13),material(warm,.5,3))
	light(Vector3(-1,2.45,.4),warm,3.6,6)
	light(Vector3(2.2,1.5,.65),Color("b6eadb"),2.1,3.5)
	lettering("AFTER THE RAIN",Vector3(-1.25,2.66,1.13),36,Color("ffdda2"))
	lettering("HOT DRINKS",Vector3(2.2,1.98,.32),20,Color("ffdc9a"))
	# Route marker and quiet timetable.
	var teal := material(Color("254c51"),.35)
	box(Vector3(-4.5,1.6,.4),Vector3(.1,3.2,.1),teal,true)
	box(Vector3(-4.5,2.9,.4),Vector3(.85,.75,.1),teal)
	lettering("08",Vector3(-4.5,3.0,.465),76,Color("f9dfab"))
	lettering("NIGHT LINE",Vector3(-4.5,2.72,.465),20,Color("d4e5db"))
	box(Vector3(-2.65,1.65,-1.08),Vector3(.62,.8,.03),material(Color("c3c9ad")))
	lettering("08 / 23\n\nTAKE YOUR TIME\n\n23:40   00:10",Vector3(-2.65,1.65,-1.055),17,Color("1c3d42"))
	# Distant silhouettes and sparse lit windows.
	for i in range(15):
		var x := float(i-7)*5
		var height := rng.randf_range(4,12)
		var building_z := -15-rng.randf_range(0,6)
		box(Vector3(x,height/2,building_z),Vector3(4,height,4),material(Color("1b2c3b")))
		for w in range(3):
			for h in range(int(height/1.5)):
				if rng.randf() < .32:
					box(Vector3(x-1.2+w*1.1,1.2+h*1.5,building_z+2.02),Vector3(.45,.65,.03),material(Color("ae9a72"),.8,.5))
	# Across the road: a quiet row of homes to watch while seated.
	for i in range(9):
		var x := float(i-4)*4.5
		var h := rng.randf_range(3.5,7)
		box(Vector3(x,h/2,23),Vector3(4,h,4),material(Color("1c303d")))
		for w in range(2):
			for floor_index in range(3):
				if rng.randf() < .65:
					box(Vector3(x-.9+w*1.8,1.3+floor_index*1.55,20.98),Vector3(.55,.7,.025),material(Color("8b8670"),.8,.35))
	for x in [-7.0,7.0]:
		box(Vector3(x,2.7,15),Vector3(.1,5.4,.1),teal)
		box(Vector3(x,5.4,15),Vector3(.7,.12,.7),teal)
		box(Vector3(x,5.32,15),Vector3(.5,.03,.5),material(warm,.5,3))
		light(Vector3(x,5,15),warm,3,8)
	for x in [-10.0,10.0]:
		box(Vector3(x,3.0,1.0),Vector3(.13,6,.13),teal)
		box(Vector3(x,6,1.6),Vector3(.6,.12,1.6),teal)
		box(Vector3(x,5.92,2),Vector3(.45,.035,.65),material(warm,.5,4))
		light(Vector3(x,5.5,2),warm,5,10)
	# Irregular reflective puddles; stylized warm light streaks.
	for i in range(38):
		var x := rng.randf_range(-16,16)
		var z := rng.randf_range(2.5,15)
		var p := MeshInstance3D.new()
		var disk := CylinderMesh.new()
		disk.top_radius = 1
		disk.bottom_radius = 1
		disk.height = .005
		disk.radial_segments = 20
		p.mesh = disk
		p.material_override = material(Color("263a47"),.06)
		add_child(p)
		p.position = Vector3(x,-.038,z)
		p.scale = Vector3(rng.randf_range(.25,1.2),1,rng.randf_range(.15,.65))
	for i in range(36):
		var z := 2.3+i*.22
		var streak := material(Color(.46,.34,.19)*(.8-i*.013),.24,.25)
		box(Vector3(-.8+sin(i*2.3)*.3,-.031,z),Vector3(rng.randf_range(.25,1.7),.005,.035),streak)
	make_rain()
	make_player()
	make_ui()
	sound = AudioStreamPlayer.new()
	sound.stream = load("res://assets/rain.wav")
	sound.volume_db = -11
	add_child(sound)
	setup_v2()
	sound.play()
	if screenshot_mode:
		player.position = Vector3(8,3.2,12)
		player.rotation.y = 0
		camera.look_at(Vector3(0,1.25,0))
	else:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if "--test" in OS.get_cmdline_user_args():
		call_deferred("self_test")

func make_player():
	player = CharacterBody3D.new()
	add_child(player)
	player.position = START
	player.rotation.y = -.85
	var col := CollisionShape3D.new()
	var shape := CapsuleShape3D.new()
	shape.radius = .24
	shape.height = 1.6
	col.shape = shape
	col.position.y = -.7
	player.add_child(col)
	camera = Camera3D.new()
	camera.fov = 67
	player.add_child(camera)
	camera.current = true

func make_ui():
	var layer := CanvasLayer.new()
	add_child(layer)
	var lower_shade := ColorRect.new()
	lower_shade.position = Vector2(0,580)
	lower_shade.size = Vector2(1280,140)
	lower_shade.color = Color(.02,.04,.055,.56)
	lower_shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(lower_shade)
	var title := Label.new()
	title.text = "AFTER THE RAIN"
	title.position = Vector2(42,30)
	title.add_theme_font_size_override("font_size",24)
	title.modulate = Color("ffe2ac")
	layer.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "A SMALL PLACE TO REST     /     23:40"
	subtitle.position = Vector2(43,65)
	subtitle.add_theme_font_size_override("font_size",12)
	subtitle.modulate = Color("a8c2c5")
	layer.add_child(subtitle)
	hint = Label.new()
	hint.position = Vector2(42,624)
	hint.add_theme_font_size_override("font_size",18)
	hint.modulate = Color("ffe8bd")
	layer.add_child(hint)
	var guide := Label.new()
	guide.text = "WASD walk   MOUSE look   E sit / board   F cocoa / sip   R restart   M mute   ESC release"
	guide.position = Vector2(42,666)
	guide.add_theme_font_size_override("font_size",14)
	guide.modulate = Color("acc5ca")
	layer.add_child(guide)

func make_rain():
	rain = MultiMeshInstance3D.new()
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	var drop := BoxMesh.new()
	drop.size = Vector3(.009,.22,.009)
	mm.mesh = drop
	mm.instance_count = 1400
	rain.multimesh = mm
	var m := material(Color("728b9b"),.4,.3)
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rain.material_override = m
	add_child(rain)
	for i in range(mm.instance_count):
		drops.append(Vector3(rng.randf_range(-18,18),rng.randf_range(0,13),rng.randf_range(-8,20)))

func _unhandled_input(event):
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		if event.relative.length() < 150:
			if has_cup:
				cup.impulse(Vector2(-event.relative.x,event.relative.y)*.02)
			player.rotation.y -= event.relative.x*.002
		if event.relative.length() < 150:
			camera.rotation.x = clamp(camera.rotation.x-event.relative.y*.002,-1.15,1.15)
	if event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		if event.keycode == KEY_E:
			interact()
		if event.keycode == KEY_F:
			drink_action()
		if event.keycode == KEY_R:
			restart()
		if event.keycode == KEY_F12:
			capture_preview()
		if event.keycode == KEY_P and not boarded:
			photo_mode = true
			seated = false
			player.position = Vector3(5.5,2.7,10)
			player.rotation.y = 0
			camera.look_at(Vector3(0,1.2,0))
		if event.keycode == KEY_M:
			muted = not muted
			AudioServer.set_bus_mute(0,muted)

func interact():
	if boarded:
		return
	photo_mode = false
	if seated:
		seated = false
		player.position = Vector3(-1,1.65,1.5)
	elif bus_phase == "stopped" and player.position.distance_to(DOOR) < 1.7:
		board_bus()
	elif player.position.distance_to(seat) < 2.6:
		seated = true
		player.position = seat
		player.rotation.y = PI
		camera.rotation = Vector3(-.04,0,0)

func _physics_process(_delta):
	if not player or screenshot_mode or photo_mode or boarded:
		return
	if not seated:
		var v := Vector3(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),0,float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W)))
		v = player.basis*v.normalized()*2.4
		if player.position.z < 2.5 and player.position.z > 1.95 and v.z < 0 and player.is_on_floor():
			player.position.y = max(player.position.y,1.64)
		player.velocity = Vector3(v.x,-1.0,v.z)
		player.move_and_slide()
		player.position.x = clamp(player.position.x,-16,16)
		player.position.z = clamp(player.position.z,-.8,2.65) # Safe curb; bus lane is separated.

func _process(delta):
	time += delta
	if hint:
		update_hint()
	if bus:
		update_v2(delta)
	for i in range(drops.size()):
		var p := drops[i]
		p.y -= delta*8
		p.x -= delta*.8
		if p.y < .12:
			p.y += 13
		if p.x < -18:
			p.x += 36
		drops[i] = p
		var hidden: bool = abs(p.x)<3.6 and abs(p.z)<1.4 and p.y<3.15
		rain.multimesh.set_instance_transform(i,Transform3D(Basis().scaled(Vector3.ZERO if hidden else Vector3.ONE),p))
	if screenshot_mode and time > 2:
		get_viewport().get_texture().get_image().save_png("res://preview.png")
		sound.stop()
		get_tree().quit()

func self_test():
	player.position = Vector3(-1,1.65,1.5)
	interact()
	assert(seated and player.position == seat)
	drink_action()
	assert(sips == 0, "Cannot buy remotely")
	interact()
	assert(not seated)
	player.position = VENDING
	drink_action()
	drink_action()
	assert(dispensing > 0 and sips == 0, "One dispense at a time")
	update_v2(1.5)
	assert(sips == 3 and cup.visible)
	player.position = Vector3(-1,1.65,1.5)
	interact()
	drink_action()
	drink_action()
	assert(sips == 2 and seated, "Sip debounced; seated drinking")
	update_v2(1.5)
	drink_action()
	update_v2(1.5)
	drink_action()
	assert(sips == 0)
	assert(rain_filter.cutoff_hz < 2500, "Roof softens rain")
	update_v2(1.5)
	interact()
	player.position = VENDING
	drink_action()
	update_v2(1.5)
	assert(sips == 3, "Can refill empty cup")
	player.position = Vector3(0,1.65,4.3)
	_physics_process(.016)
	assert(player.position.z <= 2.651, "Safe walking boundary")
	restart()
	assert(not boarded and not seated and sips == 0 and bus_phase == "waiting")
	advance_bus(26)
	assert(bus_phase == "approaching")
	advance_bus(9)
	assert(bus_phase == "stopped")
	player.position = DOOR
	interact()
	assert(boarded and ending.visible)
	drink_action()
	assert(sips == 0)
	restart()
	advance_bus(26)
	advance_bus(9)
	advance_bus(21)
	assert(bus_phase == "departing", "Can let bus pass")
	advance_bus(9)
	assert(bus_phase == "waiting", "Another bus follows")
	assert(cup.get_parent() == camera and get_node("NightBus") == bus)
	restart()
	await get_tree().create_timer(.4).timeout
	assert(player.position.y > .5)
	cup.set_fill(1.0,true)
	for up in [Vector3.UP, Vector3(.6,.8,0), Vector3(-.6,.8,.5), Vector3(1,.01,1)]:
		for frame in range(20):
			cup.impulse(Vector2(.2,-.2))
			cup.update_liquid(1.0/60.0,up)
		assert(cup.max_surface_height <= .076, "Liquid stays below rim at extreme tilt")
	cup.set_fill(0,true)
	assert(cup.current_fill == 0, "Empty resets liquid")
	for audio_node in [sound,chime,engine]:
		audio_node.stop()
		audio_node.stream = null
	await get_tree().create_timer(.5).timeout
	print("V3 TEST PASS: dispense debounce, 3 sips, seated drink, board, pass/repeat, full reset, stable objects, floor; no errors")
	get_tree().quit()

func capture_preview():
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://preview.png")
	print("Preview saved to preview.png")

func setup_v2():
	bus = Node3D.new()
	bus.name = "NightBus"
	bus.set_script(load("res://bus_visual.gd"))
	add_child(bus)
	bus.position = Vector3(-34,0,4.3)
	var layer := CanvasLayer.new()
	add_child(layer)
	bus_status = Label.new()
	bus_status.position = Vector2(900,36)
	bus_status.add_theme_font_size_override("font_size",17)
	bus_status.modulate = Color("ffe2ac")
	layer.add_child(bus_status)
	feeling = Label.new()
	feeling.position = Vector2(42,594)
	feeling.add_theme_font_size_override("font_size",14)
	feeling.modulate = Color("b7ced0")
	layer.add_child(feeling)
	ending = Control.new()
	ending.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(ending)
	var shade := ColorRect.new()
	shade.color = Color(.035,.06,.08,.92)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ending.add_child(shade)
	var message := Label.new()
	message.text = "08  /  HOME\n\nThe doors close softly.\nFor now, there is nothing else to do.\n\n[R] Another rainy evening"
	message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	message.add_theme_font_size_override("font_size",26)
	message.modulate = Color("ffe1ad")
	ending.add_child(message)
	ending.hide()
	cup = Node3D.new()
	cup.set_script(load("res://liquid_cup.gd"))
	camera.add_child(cup)
	cup.position = Vector3(.28,-.32,-.6)
	for i in range(5):
		var puff := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = .008
		sphere.height = .036
		puff.mesh = sphere
		var m := material(Color(.8,.86,.83,.12))
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		puff.material_override = m
		cup.add_child(puff)
		steam.append(puff)
	cup.hide()
	AudioServer.add_bus()
	var bus_index := AudioServer.bus_count-1
	AudioServer.set_bus_name(bus_index,"ShelterRain")
	rain_filter = AudioEffectLowPassFilter.new()
	rain_filter.cutoff_hz = 12000
	AudioServer.add_bus_effect(bus_index,rain_filter)
	sound.bus = "ShelterRain"
	chime = AudioStreamPlayer.new()
	chime.stream = load("res://assets/chime.wav")
	chime.volume_db = -15
	add_child(chime)
	engine = AudioStreamPlayer.new()
	engine.stream = load("res://assets/engine.wav")
	engine.volume_db = -40
	add_child(engine)
	engine.play()

func update_hint():
	if boarded:
		hint.text = ""
		return
	if seated:
		hint.text = "[E] Stand up" + ("     [F] Sip warm cocoa" if sips > 0 else "     Stay a while. There's no hurry.")
	elif bus_phase == "stopped" and player.position.distance_to(DOOR)<1.7:
		hint.text = "[E] Board the 08 home     /     Or let this one pass."
	elif player.position.distance_to(VENDING)<1.8:
		hint.text = "Preparing your cocoa..." if dispensing>0 else ("[F] Sip warm cocoa" if sips>0 else "[F] Get a hot cocoa  /  on the house tonight")
	elif player.position.distance_to(seat)<2.6:
		hint.text = "[E] Sit and listen" + ("     [F] Sip cocoa" if sips>0 else "")
	else:
		hint.text = "[F] Sip warm cocoa" if sips>0 else "A warm drink might be nice. The machine is still on."

func drink_action():
	if boarded or dispensing > 0 or sip_time > 0:
		return
	if sips > 0:
		sips -= 1
		sip_time = 1.3
		fill_pending = true
		cup.impulse(Vector2(.2,.9))
		warmth = 45
		note = "Warm hands. A small sweetness." if sips>0 else "The last sip. A little warmer now."
		note_time = 5
	elif player.position.distance_to(VENDING) < 1.8 and not seated:
		dispensing = 1.2
		note = "A cup drops into the tray."
		note_time = 3
		chime.play()

func update_v2(delta: float):
	if not boarded and not testing:
		advance_bus(delta)
	if dispensing > 0:
		dispensing -= delta
		if dispensing <= 0:
			sips = 3
			has_cup = true
			cup.set_fill(1.0,true)
			cup.show()
			note = "Hot cocoa. Just what your hands needed."
			note_time = 5
	if sip_time > 0:
		sip_time = maxf(0,sip_time-delta)
	if fill_pending and sip_time <= .8:
		cup.set_fill(float(sips)/3.0)
		fill_pending = false
	var sip_angle := .28 + (.38*sin((1.0-sip_time/1.3)*PI) if sip_time>0 else 0.0)
	cup.global_rotation = Vector3(sip_angle,player.rotation.y,0)
	var local_walk := player.basis.inverse()*player.velocity
	var walk := Vector2(local_walk.x,local_walk.z) if not seated else Vector2.ZERO
	cup.impulse((walk-previous_walk)*.4)
	previous_walk = walk
	cup.update_liquid(delta,cup.global_basis.inverse()*Vector3.UP)
	cup.position = cup.position.lerp(Vector3(.08,-.12,-.36) if sip_time>0 else Vector3(.28,-.32,-.6),minf(delta*6,1))
	cup.visible = has_cup and not boarded
	for i in range(steam.size()):
		var t := fmod(time*.35+i*.08,.4)
		steam[i].position = Vector3(sin(t*15+i)*.018,.07+t,0)
		steam[i].visible = sips>0
	warmth = maxf(0,warmth-delta)
	note_time = maxf(0,note_time-delta)
	var sheltered: bool = absf(player.position.x)<3.6 and absf(player.position.z)<1.4
	var cutoff := 1700.0 if sheltered or boarded else 12000.0
	rain_filter.cutoff_hz = lerpf(rain_filter.cutoff_hz,cutoff,minf(delta*2,1))
	sound.volume_db = lerpf(sound.volume_db,-23.0 if boarded else (-18.0 if sheltered else -11.0),minf(delta*2,1))
	engine.volume_db = lerpf(engine.volume_db,-25.0 if bus_phase == "stopped" else (-29.0 if bus_phase in ["approaching","departing"] else -65.0),minf(delta*2,1))
	feeling.text = "" if boarded else (note if note_time>0 else ("The rain is softer beneath the roof." if sheltered else ("The cocoa's warmth lingers." if warmth>0 else "Cool rain on your sleeves. The shelter is close.")))
	match bus_phase:
		"waiting": bus_status.text = "08  HOME  /  %02ds" % maxi(0,int(25-phase_time))
		"approaching": bus_status.text = "08  HOME  /  arriving"
		"stopped": bus_status.text = "08  HOME  /  doors open"
		"departing": bus_status.text = "08  HOME  /  see you soon"

func advance_bus(delta: float):
	phase_time += delta
	match bus_phase:
		"waiting":
			bus.position.x = -34
			if phase_time >= 25:
				bus_phase = "approaching"
				phase_time = 0
		"approaching":
			var t := minf(phase_time/8.0,1)
			bus.position.x = lerpf(-34,0,1-pow(1-t,2))
			if phase_time >= 8:
				bus.position.x = 0
				bus_phase = "stopped"
				phase_time = 0
				bus.set_door_open(true)
				chime.play()
		"stopped":
			if phase_time >= 20:
				bus_phase = "departing"
				phase_time = 0
				bus.set_door_open(false)
		"departing":
			bus.position.x = 36*pow(minf(phase_time/8.0,1),2)
			if phase_time >= 8:
				bus_phase = "waiting"
				phase_time = 0

func board_bus():
	if boarded or seated or bus_phase != "stopped":
		return
	boarded = true
	ending.show()
	cup.hide()
	bus.set_door_open(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func restart():
	boarded = false
	seated = false
	photo_mode = false
	player.position = START
	player.rotation = Vector3(0,-.85,0)
	camera.rotation = Vector3.ZERO
	player.velocity = Vector3.ZERO
	sips = 0
	has_cup = false
	fill_pending = false
	previous_walk = Vector2.ZERO
	cup.set_fill(0,true)
	dispensing = 0
	sip_time = 0
	warmth = 0
	note = "Just one more stop, then home."
	note_time = 7
	ending.hide()
	cup.hide()
	bus_phase = "waiting"
	phase_time = 0
	bus.position.x = -34
	bus.set_door_open(false)
	if not testing:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
