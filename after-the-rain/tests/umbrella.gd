extends SceneTree
var changes := 0
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var scene := load("res://scenes/held_umbrella.tscn") as PackedScene
	assert(scene != null)
	var a = scene.instantiate()
	var b = scene.instantiate()
	root.add_child(a)
	root.add_child(b)
	await process_frame
	assert(not a.held and not a.is_open and not a.visible)
	a.state_changed.connect(func(_held, _open): changes += 1)
	a.toggle_open()
	assert(changes == 0)
	a.borrow()
	a.borrow()
	assert(changes == 1 and a.held and not a.is_open and a.visible)
	assert(not b.held and not b.visible)
	assert(a.get_node("FoldedCanopy").visible and not a.get_node("OpenCanopy").visible)
	for i in range(100):
		a.toggle_open()
		assert(a.is_open == (i % 2 == 0))
		assert(a.get_node("OpenCanopy").visible == a.is_open)
	assert(changes == 101 and not a.is_open)
	a.toggle_open()
	var rest: Vector3 = a.position
	for i in range(120):
		a.present(.016, Vector3(1000, 500, -1000))
		assert(absf(a.position.x - rest.x) <= a.sway_amount + .00001)
		assert(absf(a.position.y - rest.y) <= a.sway_amount * .5 + .00001)
		assert(a.position.z == rest.z)
	assert(b.position == rest)
	# Every open fabric vertex lies above the camera and the cocoa's upper bound.
	for panel in a.get_node("OpenCanopy").get_children():
		if panel.name.begins_with("Panel"):
			for vertex in panel.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]:
				assert((vertex + rest).y >= .67)
	for i in range(240):
		a.present(.016, Vector3.ZERO)
	assert(a.position.distance_to(rest) < .0001)
	a.return_umbrella()
	assert(not a.held and not a.is_open and not a.visible and a.position == rest)
	a.borrow()
	a.toggle_open()
	a.reset()
	assert(not a.held and not a.is_open and not a.visible)
	b.borrow()
	assert(b.held and not a.held)
	var packed := PackedScene.new()
	assert(packed.pack(a) == OK)
	assert(ResourceSaver.save(packed,"/tmp/v7-umbrella-roundtrip.tscn") == OK)
	var reopened = load("/tmp/v7-umbrella-roundtrip.tscn").instantiate()
	assert(reopened.has_node("OpenCanopy/Panel00") and reopened.has_node("Shaft"))
	reopened.free()
	a.queue_free()
	b.queue_free()
	await process_frame
	print("UMBRELLA PASS: authored standalone, independent state, repeated toggle, bounded sway, settle/reset, canopy clearance, saved children")
	quit()
