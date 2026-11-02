extends SceneTree
func _initialize(): call_deferred("run")
func run():
	var story = load("res://scenes/story_corner.tscn").instantiate()
	root.add_child(story)
	var camera := Camera3D.new()
	root.add_child(camera)
	var radio = story.objects.get_node("Radio")
	var marker: Vector3 = radio.get_node("Interaction").global_position
	var body: Vector3 = radio.get_node("RadioBody").global_position
	assert(is_equal_approx(body.y,.92) and is_equal_approx(marker.y,body.y), "Radio targeting matches real body")
	assert(marker.is_equal_approx(Vector3(.95,.92,.37)))
	assert(story.radio.global_position.is_equal_approx(marker), "3D sound anchored to visible radio")
	assert(story.threshold_for("Memo")==.95 and story.threshold_for("Route")==.95)
	assert(story.threshold_for("Radio")==.94 and story.threshold_for("Passenger")==.72)
	for id in ["Memo","Route","Radio","Passenger"]:
		var target: Vector3 = story.objects.get_node(id+"/Interaction").global_position
		camera.global_position = target+Vector3(0,0,1.4)
		camera.look_at(target)
		assert(story.target(camera,camera.global_position)==id, "Direct gaze: "+id)
		var threshold: float = story.threshold_for(id)
		var inside_angle := acos(threshold+.015)
		camera.rotation.y = inside_angle
		assert(story.target(camera,camera.global_position)==id, "Inside target-specific cone: "+id)
		camera.rotation.y = acos(threshold-.015)
		assert(story.target(camera,camera.global_position)!=id, "Outside target-specific cone: "+id)
		camera.global_position = target+Vector3(0,0,2.5)
		camera.look_at(target)
		assert(story.target(camera,camera.global_position)!=id, "Reach gate: "+id)
	camera.global_position = marker+Vector3(0,.6,1.0)
	camera.look_at(body+Vector3(0,0,.12))
	assert(story.target(camera,camera.global_position)=="Radio", "Looking at radio itself works")
	assert(story.try_interact(camera,camera.global_position) and story.radio.is_on)
	assert(not story.panel.is_open, "Radio remains optional toggle, not forced reader")
	story.reset()
	assert(not story.radio.is_on)
	story.free()
	camera.free()
	await create_timer(.2).timeout
	print("RECOVERY RADIO TARGET PASS: actual body/audio height, per-target cones, reach, optional toggle/reset")
	quit()
