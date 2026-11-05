extends SceneTree
var checks := 0
func check(value: bool, message: String) -> void:
	checks += 1
	if not value:
		push_error("RECOVERY WEATHER FAIL: " + message)
		quit(1)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var weather = load("res://scenes/weather_cycle.tscn").instantiate()
	var other_weather = load("res://scenes/weather_cycle.tscn").instantiate()
	root.add_child(weather)
	root.add_child(other_weather)
	for pair in [[0.,0.],[45.,0.],[51.,.5],[57.,1.],[75.,1.],[81.,.5],[87.,0.],[180.,0.],[237.,1.]]:
		weather.present(pair[0])
		check(is_equal_approx(weather.strength,pair[1]), "Weather timeline ramps/hold/repeat")
	weather.present(1000000.0)
	check(weather.phase >= 0 and weather.phase < 180 and weather.strength >= 0 and weather.strength <= 1, "Long deterministic clock bounded")
	check(other_weather.strength == 0 and other_weather.phase == 0, "Weather instances isolated")
	weather.reset()
	await process_frame
	check(weather.phase == 0 and weather.strength == 0, "Reset and no automatic clock")
	var rain = load("res://scenes/rain.tscn").instantiate()
	var other = load("res://scenes/rain.tscn").instantiate()
	root.add_child(rain)
	root.add_child(other)
	check(rain.drops == other.drops and rain.drops.size() == 1400, "Original deterministic fallback population")
	rain.set_weather(1)
	check(rain.instances.multimesh.visible_instance_count == 812, "Full lull visible count")
	check(other.instances.multimesh.visible_instance_count == 1400, "Population instance isolation")
	for i in range(120):
		rain.advance(.1)
		other.advance(.1)
	check(rain.drops == other.drops, "All hidden trajectories continue stepping without RNG changes")
	rain.set_weather(0)
	check(rain.instances.multimesh.visible_instance_count == 1400 and rain.drops == other.drops, "Full rain restores same trajectories")
	var flower := Node3D.new()
	flower.position = Vector3(-9,0,-6)
	root.add_child(flower)
	var cover = load("res://scenes/rain_cover.tscn").instantiate()
	flower.add_child(cover)
	var bounds: AABB = cover.get_world_bounds()
	check(bounds.position.is_equal_approx(Vector3(-10.825,0,-6.12)) and bounds.size.is_equal_approx(Vector3(3.65,2.605,1)), "Exact saved awning world dry volume")
	var world = load("res://scripts/world.gd").new()
	var stop := Node3D.new()
	stop.name = "BusStop"
	var anchors := Node3D.new()
	anchors.name = "Anchors"
	stop.add_child(anchors)
	world.add_child(stop)
	root.add_child(world)
	var shelters: Array[AABB] = [bounds]
	world.additional_shelters = shelters
	rain.additional_shelters = shelters
	check(world.is_sheltered(Vector3(-9,1.65,-5.6)), "Player sheltered under actual awning")
	check(not world.is_sheltered(Vector3(-9,2.7,-5.6)) and not world.is_sheltered(Vector3(-9,1.65,-4.9)), "No protection above/beyond awning")
	check(world.is_sheltered(Vector3(0,9,0)) and not world.is_sheltered(Vector3(3.61,1,0)), "Existing shelter semantics unchanged")
	var positions: Array[Vector3] = [Vector3(-9,1.65,-5.6),Vector3(-9,2.7,-5.6),Vector3(0,2,0),Vector3(5,2,0)]
	rain.initialize(positions)
	check(rain._drop_hidden(positions[0]), "Rain hidden in injected dry bounds")
	check(not rain._drop_hidden(positions[1]), "Rain above awning visible")
	check(rain._drop_hidden(positions[2]), "Original roof rain exclusion unchanged")
	check(not rain._drop_hidden(positions[3]), "Outside rain unaffected")
	flower.rotation.y = .5
	flower.scale = Vector3(1.2,1,1)
	var transformed: AABB = cover.get_world_bounds()
	for x in [-1.825,1.825]:
		for y in [-1.3025,1.3025]:
			for z in [-.5,.5]:
				var point: Vector3 = cover.global_transform * Vector3(x,y,z)
				check(transformed.grow(.0001).has_point(point), "Transformed cover encloses all eight corners")
	var ambience = load("res://scenes/ambience.tscn").instantiate()
	root.add_child(ambience)
	ambience.set_weather(0)
	ambience.advance(1,false,false,"stopped")
	var engine_db: float = ambience.engine_player.volume_db
	var canopy_db: float = ambience.canopy_player.volume_db
	ambience.set_weather(1)
	ambience.advance(1,false,false,"stopped")
	check(is_equal_approx(ambience.rain_player.volume_db,ambience.outside_rain_db-4.5), "Lull reduces rain-only target4.5dB")
	check(ambience.engine_player.volume_db == engine_db and ambience.canopy_player.volume_db == canopy_db, "Engine and canopy levels unchanged by weather")
	ambience.reset()
	check(ambience.weather_lull == 0 and ambience.rain_player.volume_db == ambience.outside_rain_db, "Audio weather reset")
	ambience.stop_all()
	for node in [weather,other_weather,rain,other,flower,world,ambience]: node.queue_free()
	await process_frame
	print("RECOVERY WEATHER PASS: ",checks," checks")
	quit()
