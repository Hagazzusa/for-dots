extends SceneTree
var checks := 0
var failures := 0
func check(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error("BUS CLARITY FAIL: " + message)
func bounds(node: MeshInstance3D) -> AABB:
	return node.global_transform * node.get_aabb()
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var scene = load("res://scenes/bus_visual.tscn")
	var bus = scene.instantiate()
	var other = scene.instantiate()
	root.add_child(bus)
	root.add_child(other)
	check(not bus.has_node("InteriorWarmPanel"), "Bright wall removed")
	check(bus.get_node("EntryUpperStep").position.is_equal_approx(Vector3(2.8,.7,-.8)), "Upper step unchanged location")
	check(bus.get_node("EntryUpperStep").mesh.size.is_equal_approx(Vector3(1.3,.15,.7)), "Upper step unchanged dimensions")
	check(bus.get_node("EntryLowerStep").position.is_equal_approx(Vector3(2.8,.5,-1)), "Lower step unchanged location")
	for name in ["EntryUpperStep","EntryLowerStep"]:
		check(not bus.get_node(name).material_override.emission_enabled, "Steps nonemissive")
	var light = bus.get_node("EntryLight")
	check(light.position.is_equal_approx(Vector3(2.8,2.3,-.25)) and is_equal_approx(light.light_energy,.75) and is_equal_approx(light.omni_range,3.8), "Restrained existing lamp moved inside")
	check(bus.find_children("*","Light3D",true,false).size() == 3, "No added lights")
	check(bus.find_children("*","CollisionObject3D",true,false).is_empty(), "No new collision")
	var details = bus.get_node("EntryDetails")
	check(details.get_child_count() == 7, "Seven authored entry details")
	var triangles := 0
	for part in details.get_children():
		check(part is MeshInstance3D and part.material_override is BaseMaterial3D, "Private fade compatible")
		triangles += int(part.mesh.get_faces().size()/3.0)
		var box: AABB = bounds(part)
		check(box.position.x > 2.14 and box.end.x < 3.46 and box.position.y > .55 and box.end.y < 2.49, "Entry details bounded")
		for wheel in ["FrontWheelCurb","FrontWheelRoad","RearWheelCurb","RearWheelRoad"]:
			check(not box.intersects(bounds(bus.get_node(wheel))), "Added details clear wheels")
		for second in details.get_children():
			if second != part:
				check(not box.intersects(bounds(second)), "Details do not intersect each other")
	check(triangles <= 120, "Triangle budget <=120")
	check(is_equal_approx(bounds(bus.get_node("EntryLowerStep")).position.x-bounds(bus.get_node("FrontWheelCurb")).end.x,.32), "Original .32m tire-step clearance")
	for phase in range(2):
		for sample in range(11):
			var t := sample/10.0
			for i in range(2):
				var leaf = bus.doors[i]
				leaf.position.x = bus.CLOSED_X[i] if phase == 0 else lerpf(bus.CLOSED_X[i],bus.OPEN_X[i],t)
				leaf.position.z = lerpf(bus.CLOSED_Z,bus.POCKET_Z[i],t) if phase == 0 else bus.POCKET_Z[i]
				for part in leaf.get_children():
					for wheel in ["FrontWheelCurb","FrontWheelRoad","RearWheelCurb","RearWheelRoad"]:
						check(not bounds(part).intersects(bounds(bus.get_node(wheel))), "Door sweep still clears every wheel")
	var lens = details.get_node("CeilingLens")
	var original = lens.material_override
	# Material storage can round authored 0.3 to float32 0.300000012.
	check(is_equal_approx(original.emission_energy_multiplier, .3), "Small lens authored restrained emission0.3")
	bus.set_route_opacity(.25)
	for part in details.get_children():
		check(part.material_override != other.get_node("EntryDetails/"+str(part.name)).material_override, "New details have private fade resources")
	check(is_equal_approx(other.get_node("EntryLight").light_energy,.75), "Other instance lamp isolated")
	bus.set_route_opacity(0)
	check(not bus.visible and not light.visible and light.light_energy == 0, "Waiting hides full revised entry")
	bus.set_route_opacity(1)
	check(lens.material_override == original and is_equal_approx(light.light_energy,.75), "Opaque route restores authored resources")
	bus.queue_free()
	other.queue_free()
	await process_frame
	print("RECOVERY BUS CLARITY: ",checks," checks, ",failures," failures; 7 meshes / ",triangles," triangles")
	quit(1 if failures else 0)
