extends SceneTree
var bus: Node3D
var checks := 0
func bounds(mesh: MeshInstance3D) -> AABB:
	return mesh.global_transform * mesh.get_aabb()
func check_clearance():
	for wheel_name in ["FrontWheelCurb", "FrontWheelRoad", "RearWheelCurb", "RearWheelRoad"]:
		var wheel = bounds(bus.get_node(wheel_name))
		for leaf in bus.doors:
			for part in leaf.get_children():
				assert(not bounds(part).intersects(wheel), "Door part intersects " + wheel_name)
		for step_name in ["EntryUpperStep", "EntryLowerStep"]:
			assert(not bounds(bus.get_node(step_name)).intersects(wheel), "Step intersects " + wheel_name)
	checks += 1
func _initialize():
	call_deferred("run")
func run():
	bus = load("res://scenes/bus_visual.tscn").instantiate()
	root.add_child(bus)
	check_clearance()
	var tire = bounds(bus.get_node("FrontWheelCurb"))
	var step = bounds(bus.get_node("EntryLowerStep"))
	assert(is_equal_approx(step.position.x - tire.end.x, .32))
	assert(is_equal_approx(step.get_center().x, 2.8))
	for opened in [true, false]:
		bus.set_door_open(opened)
		while bus.door_tween.is_running():
			await process_frame
			check_clearance()
		for leaf in bus.doors:
			var b = bounds(leaf.get_node("Panel"))
			assert(b.end.x <= 3.45)
			if opened:
				assert(b.end.x < 2.15)
	# Mid-animation reversal also remains clear.
	bus.set_door_open(true)
	await create_timer(.4).timeout
	bus.set_door_open(false)
	while bus.door_tween.is_running():
		await process_frame
		check_clearance()
	bus.queue_free()
	await process_frame
	print("BUS CLEARANCE PASS: actual 3D mesh bounds, closed/open/transit/reversal, steps, 0.32m front-tire gap; samples=", checks)
	quit()
