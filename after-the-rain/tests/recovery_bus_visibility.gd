extends SceneTree
## Reconstructed visibility regression gate; no unavailable snapshot dependency.
var checks := 0
func check(value: bool, message: String) -> void:
	checks += 1
	assert(value, message)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var scene = load("res://scenes/night_bus.tscn")
	var a = scene.instantiate()
	var b = scene.instantiate()
	var alone = load("res://scenes/bus_visual.tscn").instantiate()
	for node in [a,b,alone]: root.add_child(node)
	check(alone.visible and alone.route_opacity == 1, "Standalone saved visual remains visible")
	check(a.visible and not a.visual.visible and a.position.x == a.schedule.approach_x, "Waiting hides only child visual")
	check(a.visual._fade_meshes.size() == 87, "Every authored mesh cached")
	check(a.visual._fade_lights.size() == 3, "All authored lights cached")
	check(a.find_children("*","CollisionObject3D",true,false).is_empty(), "No added collision")
	for lamp in a.visual._fade_lights:
		check(not lamp.node.visible and lamp.node.light_energy == 0, "No waiting light spill")
	var entry: Dictionary = a.visual._fade_meshes[0]
	var original: BaseMaterial3D = entry.original
	var faded: BaseMaterial3D = entry.faded
	var color: Color = original.albedo_color
	var mode: int = original.transparency
	check(faded != b.visual._fade_meshes[0].faded, "Private fade material per instance")
	for cycle in range(3):
		a.advance(a.schedule.wait_seconds + 17)
		check(a.phase == "approaching" and a.phase_time == 0, "Original single-transition excess-delta behavior")
		check(not a.visual.visible and a.position.x == a.schedule.approach_x, "Invisible approach endpoint")
		a.advance(.5)
		check(a.visual.route_opacity > 0 and a.visual.route_opacity < 1, "Smooth distant approach")
		check(entry.node.material_override == faded, "Cached fade reused")
		check(not b.visual.visible and alone.route_opacity == 1, "Other instances unaffected")
		a.advance(3.5)
		check(a.visual.route_opacity == 1 and entry.node.material_override == original, "Opaque playable area restores authored material")
		a.advance(4)
		check(a.phase == "stopped" and a.visual.door_open and a.position.x == a.schedule.stop_x, "Original stop timing and door state")
		for lamp in a.visual._fade_lights:
			check(lamp.node.light_energy == lamp.energy and lamp.node.visible == lamp.visible, "Authored lamp restored")
		a.advance(a.schedule.stop_seconds)
		check(a.phase == "departing" and not a.visual.door_open, "Original departure and door closing")
		a.advance(7)
		check(a.visual.route_opacity > 0 and a.visual.route_opacity < 1, "Smooth distant departure")
		a.advance(1)
		check(a.phase == "waiting" and not a.visual.visible and a.position.x == a.schedule.departure_x, "Hidden before waiting teleport")
		a.advance(0)
		check(a.position.x == a.schedule.approach_x and not a.visual.visible, "Waiting relocation invisible")
	check(original.albedo_color == color and original.transparency == mode, "Shared original untouched")
	check(entry.faded == faded, "No fade-resource churn across cycles")
	a.advance(a.schedule.wait_seconds)
	a.advance(a.schedule.approach_seconds)
	a.hide()
	a.set_paused(true)
	a.advance(1000)
	check(not a.visible and not a.visual.is_visible_in_tree() and a.phase == "stopped", "Boarded hidden root stays hidden and paused")
	a.reset()
	check(not a.visible and not a.visual.visible and not a.paused and a.phase_time == 0, "Reset preserves root visibility ownership")
	a.show()
	a.advance(a.schedule.wait_seconds)
	a.advance(4)
	check(a.visual.is_visible_in_tree(), "Explicit root restoration allows next journey")
	a.hide()
	a.visual.set_route_opacity(.5)
	a.visual.set_route_opacity(1)
	check(not a.visible and not a.visual.is_visible_in_tree(), "Even active child fading cannot reveal boarded root")
	a.reset()
	check(not a.visual.visible and not a.visual.door_open, "Midroute reset hides and closes")
	for node in [a,b,alone]: node.queue_free()
	await process_frame
	print("RECOVERY BUS VISIBILITY PASS: ",checks," checks")
	quit()
