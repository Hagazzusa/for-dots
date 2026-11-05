extends SceneTree
func _initialize():
	call_deferred("run")
func run():
	var count = AudioServer.bus_count
	assert(AudioServer.get_bus_index("ShelterRain") == 1)
	var hud = load("res://scenes/hud.tscn").instantiate()
	root.add_child(hud)
	hud.present("TEST HINT","TEST FEELING","08 / TEST",true)
	assert(hud.hint.text == "TEST HINT" and hud.ending.visible)
	var scene = load("res://scenes/rain.tscn")
	var rain_a = scene.instantiate()
	var rain_b = scene.instantiate()
	root.add_child(rain_a)
	root.add_child(rain_b)
	rain_a.initialize([Vector3(0,2,0),Vector3(5,4,5)])
	rain_b.initialize([Vector3(1,3,1)])
	assert(rain_a.instances.multimesh != rain_b.instances.multimesh)
	assert(rain_a.drops.size() == 2 and rain_b.drops.size() == 1)
	rain_a.advance(.1)
	assert(rain_b.drops[0] == Vector3(1,3,1))
	assert(is_equal_approx(rain_a.drops[1].y,3.2))
	var audio_scene = load("res://scenes/ambience.tscn")
	for i in range(3):
		var a = audio_scene.instantiate()
		var b = audio_scene.instantiate()
		root.add_child(a)
		root.add_child(b)
		assert(AudioServer.bus_count == count)
		a.advance(1,true,false,"stopped")
		assert(a.rain_filter.cutoff_hz == 1700)
		assert(a.rain_player.volume_db == -18)
		assert(b.rain_player.volume_db == -11)
		assert(a.rain_filter == b.rain_filter) # Explicit project-wide mix.
		a.queue_free()
		b.queue_free()
		await process_frame
	assert(AudioServer.bus_count == count)
	hud.queue_free()
	rain_a.queue_free()
	rain_b.queue_free()
	await process_frame
	print("HUD/RAIN/AUDIO PASS: saved standalone scenes, independent rain/player state, shared documented filter, no bus growth after recreation")
	quit()
