extends SceneTree
func _initialize():
	call_deferred("run")
func run():
	var packed = load("res://scenes/stories/waiting_passenger.tscn")
	var a = packed.instantiate()
	var b = packed.instantiate()
	a.position = Vector3(-3.65, 0, .25)
	b.position = Vector3(20, 0, .25)
	root.add_child(a)
	root.add_child(b)
	var home = a.global_position
	var door = Vector3(2.8, 0, 3.3)
	assert(a.is_available() and a.solid.collision_layer != 0)
	a.advance(1.99, "stopped", door, true)
	assert(a.state == "wait")
	a.advance(.02, "stopped", door, true)
	assert(a.state == "walk" and not a.is_available() and a.solid.collision_layer == 0)
	assert(b.state == "wait" and b.is_available())
	# Close while on the first segment; walk back, don't teleport.
	var before = a.global_position
	a.advance(.001, "departing", door, false)
	assert(a.returning and a.global_position.distance_to(before) < .002)
	a.advance(100, "waiting", door, false)
	assert(a.state == "wait" and a.global_position.is_equal_approx(home))
	# Long deltas consume polyline segments, with finite exact arrival.
	a.advance(100, "stopped", door, true)
	assert(a.state == "boarded" and not a.visible and not a.is_available())
	for phase in ["departing", "waiting", "approaching", "stopped"]:
		a.advance(100, phase, door, false)
		assert(a.state == "boarded")
	a.reset()
	assert(a.visible and a.is_available() and a.solid.collision_layer != 0)
	# Reach the long pavement segment and reverse over authored corners.
	a.advance(4, "stopped", door, false)
	assert(a.state == "walk" and a.global_position.z > 1.69)
	a.advance(.01, "departing", door, false)
	assert(a.returning)
	for i in range(100):
		a.advance(.05, "waiting", door, false)
	assert(a.is_available() and a.global_position.is_equal_approx(home))
	a.advance(100, "stopped", door, false)
	assert(a.state == "boarded")
	a.reset()
	a.leave_with_player()
	assert(not a.visible and a.state == "boarded")
	a.reset()
	assert(a.is_available())
	assert(b.global_position == Vector3(20, 0, .25) and b.is_available())
	# Authored child ownership survives packing; visual mesh paths remain stable.
	var copy := PackedScene.new()
	assert(copy.pack(a) == OK)
	var reopened = copy.instantiate()
	assert(reopened.has_node("Visual/PaperBag") and reopened.has_node("Solid/Shape"))
	reopened.free()
	a.queue_free()
	b.queue_free()
	await process_frame
	print("PASSENGER PASS: bounded dialogue delay, safe waypoint return, long delta, stays boarded, reset, two instances, collision gates, authored scene repack")
	quit()
