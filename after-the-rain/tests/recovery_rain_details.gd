extends SceneTree
var checks := 0
var failures := 0
func check(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error("RAIN DETAILS FAIL: "+message)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var scene = load("res://scenes/rain_details.tscn")
	var a = scene.instantiate()
	var b = scene.instantiate()
	var world = load("res://scenes/world.tscn").instantiate()
	for node in [a,b,world]: root.add_child(node)
	check(a.get_node("Puddles").get_child_count() == 8, "Eight authored overlays")
	check(a.find_children("*","Light3D",true,false).is_empty() and a.find_children("*","CollisionObject3D",true,false).is_empty(), "No lights or collision")
	check(a.drops.multimesh != b.drops.multimesh and a._drop_material != b._drop_material and a._impact_material != b._impact_material, "Instance-private buffers/materials")
	check(a.drops.multimesh.instance_count == 12 and a.drops.multimesh.mesh.size.is_equal_approx(Vector3(.01,.045,.01)), "Twelve fixed small drops")
	for i in range(8):
		var plane = a.get_node("Puddles").get_child(i)
		var source = world.get_node(plane.get_meta("source_puddle"))
		check(plane.position.x == source.position.x and plane.position.z == source.position.z, "Overlay centered on actual authored puddle")
		check(is_equal_approx(plane.position.y,-.034) and is_equal_approx(source.position.y+source.mesh.height*.5,-.0355), "Overlay above actual puddle surface")
		check(is_equal_approx(plane.scale.x,source.scale.x*.85) and is_equal_approx(plane.scale.z,source.scale.z*.85), "Inset within actual puddle ellipse")
		check(plane.material_override != b.get_node("Puddles").get_child(i).material_override, "Private per-plane ring material")
		check(not plane.material_override.shader.code.contains("TIME"), "No shader wall clock")
	check(a.get_node("Gutter").position.is_equal_approx(Vector3(3.7,0,1.51)), "Outlet outside shelter dry bounds")
	var spout = a.get_node("Gutter/Spout")
	var spout_bounds: AABB = spout.global_transform * spout.get_aabb()
	var actual_gutter := AABB(Vector3(-3.59,3.005,1.335),Vector3(7.18,.19,.09))
	check(spout_bounds.intersects(actual_gutter), "Small spout visibly joins verified roof gutter")
	check(is_equal_approx(a.get_node("Gutter/Impact").position.y,.103), "Impact just above .1m sidewalk")
	check(a.get_node("Gutter/Impact").scale.x <= .070001, "Tiny ground ring")
	var initial: Array[Vector3] = a.drop_positions.duplicate()
	for step in range(300):
		a.present(step*.137,0.0)
		check(a.active_drop_count <= 7 and a.active_drop_count >= 6, "Bounded staggered stream")
		for i in range(12):
			if not a.is_drop_active(i): continue
			var point: Vector3 = a.get_drop_position(i)
			check(absf(point.x) <= .020001 and absf(point.z) <= .020001, "Narrow drop spread")
			check(point.y >= .1254 and point.y <= 2.9801, "Drop bounds stay below outlet/above pavement")
			var global_point: Vector3 = a.get_node("Gutter").to_global(point)
			check(global_point.x > 3.6 and global_point.z > 1.4, "No drops inside original dry shelter")
	check(b.elapsed == 0 and b.drop_positions == initial, "Second instance unchanged")
	a.present(1000000.25,1.0)
	check(a.phase >= 0 and a.phase < 1 and a.lull == 1 and is_equal_approx(a._drop_material.albedo_color.a,.22), "Long clock/lull opacity bounded")
	var positions: Array[Vector3] = a.drop_positions.duplicate()
	a.present(1000000.25,0.0)
	check(a.drop_positions == positions and is_equal_approx(a._drop_material.albedo_color.a,.48), "Weather changes visibility not deterministic motion")
	a.reset()
	check(a.elapsed == 0 and a.lull == 0 and a.phase == 0 and a.drop_positions == initial, "Reset deterministic")
	var material = a._ripple_materials[0]
	var mm = a.drops.multimesh
	for i in range(10): a.reset()
	check(a._ripple_materials[0] == material and a.drops.multimesh == mm, "No per-frame/reset resource allocation")
	for node in [a,b,world]: node.queue_free()
	await process_frame
	print("RECOVERY RAIN DETAILS: ",checks," checks, ",failures," failures; CPU state, not Dummy-render readback")
	quit(1 if failures else 0)
