extends SceneTree
var failures: Array[String] = []
var checks := 0
func _initialize() -> void:
	call_deferred("run")
func expect(value: bool, label: String) -> void:
	checks += 1
	if not value:
		failures.append(label)
		push_error(label)
func key(viewer: Node, code: Key, echo := false) -> void:
	var event := InputEventKey.new()
	event.keycode = code # Deliberately physical_keycode == 0, as remote keyboard events may be logical.
	event.pressed = true
	event.echo = echo
	viewer._unhandled_key_input(event)
func run() -> void:
	var packed := load("res://scenes/viewer.tscn") as PackedScene
	var viewer := packed.instantiate()
	root.add_child(viewer)
	await process_frame
	var refuge = viewer.refuge
	var rig = viewer.rig
	var lamp = viewer.pendant
	expect(refuge.panes.size() == 24, "24 imported glass panes")
	expect(refuge.globe != null, "original globe mesh resolves")
	expect(lamp.is_on and refuge.glass_visible, "default states")
	key(viewer, KEY_L)
	expect(not lamp.is_on and not lamp.light.visible, "L toggles actual light")
	key(viewer, KEY_L, true)
	expect(not lamp.is_on, "held-key echo cannot repeatedly toggle")
	key(viewer, KEY_G)
	expect(not refuge.glass_visible, "G toggles panes")
	for pane in refuge.panes:
		expect(not pane.visible, "hidden pane")
	key(viewer, KEY_R)
	expect(lamp.is_on and refuge.glass_visible, "R resets lamp and glass")
	var start: Vector3 = rig.camera.position
	for i in range(24):
		rig.orbit(TAU / 24.0, 0.0)
	expect(rig.camera.position.distance_to(start) < 0.0001, "full 360 orbit returns to starting view")
	rig.zoom_by(-1000.0)
	expect(is_equal_approx(rig.distance, 4.3), "near zoom clamp")
	rig.zoom_by(1000.0)
	expect(is_equal_approx(rig.distance, 15.0), "far zoom clamp")
	rig.orbit(0.0, 1000.0)
	expect(is_equal_approx(rig.pitch, 1.1), "upper pitch clamp")
	rig.orbit(0.0, -1000.0)
	expect(is_equal_approx(rig.pitch, -0.02), "lower pitch clamp")
	rig.dragging = true
	rig._stop_drag()
	expect(not rig.dragging, "focus-loss drag release")
	for i in range(50):
		viewer.toggle_lamp()
		viewer.toggle_glass()
	viewer.reset_all()
	expect(lamp.is_on and refuge.glass_visible, "repeated toggles/reset")
	expect(rig.camera.position.distance_to(start) < 0.0001, "reset camera")
	var second := packed.instantiate()
	root.add_child(second)
	await process_frame
	viewer.toggle_lamp()
	viewer.toggle_glass()
	expect(second.pendant.is_on and second.refuge.glass_visible, "two instances have independent state")
	expect(second.pendant.globe_material != lamp.globe_material, "globe material not shared")
	second.queue_free()
	viewer.queue_free()
	await process_frame
	var third := packed.instantiate()
	root.add_child(third)
	await process_frame
	expect(third.pendant.is_on and third.refuge.glass_visible, "free/reinstantiate resets state")
	third.queue_free()
	await process_frame
	var result := {"checks": checks, "failures": failures, "headless_logic_only": true, "rendering_and_physical_keyboard_not_verified": true}
	var f := FileAccess.open("res://qa/headless_tests.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(result, "  "))
	print("VIEWER_TEST_RESULT ", JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)
