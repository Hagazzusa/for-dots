extends SceneTree
const Baker = preload("res://scripts/city_layout.gd")
func _initialize():
	call_deferred("run")
func signature(generated: Node) -> Array:
	var result: Array = []
	for building in generated.get_children():
		result.append([building.name, building.transform, building.get_meta("city_variant"), building.scene_file_path])
	return result
func mesh_points(node: Node, transform: Transform3D, points: Array[Vector3]) -> void:
	var current = transform
	if node is Node3D:
		current = transform * node.transform
	if node is MeshInstance3D and node.mesh != null:
		var bounds = node.mesh.get_aabb()
		for i in range(8):
			points.append(current * bounds.get_endpoint(i))
	for child in node.get_children():
		mesh_points(child,current,points)
func check_geometry_envelope(building: Node3D, layout: Resource) -> void:
	var points: Array[Vector3] = []
	for child in building.get_children():
		mesh_points(child,Transform3D.IDENTITY,points)
	assert(not points.is_empty(), "Building variant has no mesh geometry")
	for point in points:
		assert(absf(point.x) <= layout.building_width*.5+.02, "Variant exceeds configured X envelope")
		assert(absf(point.z) <= layout.building_depth*.5+.02, "Variant exceeds configured Z envelope")
		assert(point.y >= -.02 and point.y <= layout.building_height+.02, "Variant exceeds configured Y envelope")
func run():
	var scene_root = Node3D.new()
	scene_root.name = "CityTest"
	root.add_child(scene_root)
	var baker = Baker.new()
	baker.name = "CityLayout"
	scene_root.add_child(baker)
	baker.owner = scene_root
	baker.layout = baker.layout.duplicate()
	var untouched = Marker3D.new()
	untouched.name = "AuthoredLandmark"
	baker.add_child(untouched)
	untouched.owner = scene_root
	assert(baker.get_node_or_null("Generated") == null, "No automatic ready generation")
	var result = baker.build(scene_root)
	if result != OK:
		push_error("CITY TEST blocked: " + "; ".join(baker.last_errors))
		quit(1)
		return
	var generated = baker.get_node("Generated")
	assert(generated.owner == scene_root)
	assert(generated.get_child_count() == 16)
	var first = signature(generated)
	for index in range(16):
		var building = generated.get_child(index)
		assert(building.owner == scene_root)
		assert(is_equal_approx(building.position.x, -28.0 + (index%8)*8.0))
		assert(building.scale.x == 1 and building.scale.z == 1)
		assert(building.scale.y >= .75 and building.scale.y <= 1.25)
		assert(building.position.z == (-14.0 if index < 8 else 23.0))
		var front = building.basis.z.normalized()
		assert(front.dot(Vector3.BACK if index < 8 else Vector3.FORWARD) > .999)
		check_geometry_envelope(building,baker.layout)
		var near_edge = building.position.z + baker.layout.building_depth*.5 if index < 8 else building.position.z - baker.layout.building_depth*.5
		assert(near_edge <= -2 if index < 8 else near_edge >= 18)
		if index%8 != 0:
			assert(building.position.x-generated.get_child(index-1).position.x >= baker.layout.building_width+baker.layout.minimum_gap)
	assert(baker.count_nodes(generated) <= baker.layout.node_budget)
	var meshes = generated.find_children("*", "MeshInstance3D", true, false)
	var surfaces = 0
	for mesh_instance in meshes:
		surfaces += mesh_instance.mesh.get_surface_count()
	print("CITY BUDGET: ", baker.count_nodes(generated), " nodes / ", baker.layout.node_budget, " cap; ", meshes.size(), " meshes; ", surfaces, " surfaces")
	assert(baker.build(scene_root) == OK)
	assert(signature(baker.get_node("Generated")) == first)
	assert(is_instance_valid(untouched) and untouched.get_parent() == baker)
	baker.layout.layout_seed += 1
	assert(baker.build(scene_root) == OK)
	assert(signature(baker.get_node("Generated")) != first)
	baker.layout.layout_seed -= 1
	assert(baker.build(scene_root) == OK)
	# Invalid authoring inputs must not destroy the last valid preview.
	for field in ["spacing","rear_row_z","across_road_z","node_budget"]:
		var old_value = baker.layout.get(field)
		baker.layout.set(field, {"spacing":1.0,"rear_row_z":0.0,"across_road_z":0.0,"node_budget":1}[field])
		assert(baker.build(scene_root) != OK)
		assert(signature(baker.get_node("Generated")) == first)
		baker.layout.set(field,old_value)
	var packed = PackedScene.new()
	assert(packed.pack(scene_root) == OK)
	assert(ResourceSaver.save(packed,"user://city_persistence_test.tscn") == OK)
	var reopened = ResourceLoader.load("user://city_persistence_test.tscn","PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	root.add_child(reopened)
	var reopened_baker = reopened.get_node("CityLayout")
	assert(signature(reopened_baker.get_node("Generated")) == first)
	assert(reopened_baker.get_node("AuthoredLandmark") != null)
	assert(reopened_baker.get_node("Generated").owner == reopened)
	for building in reopened_baker.get_node("Generated").get_children():
		assert(building.owner == reopened)
		assert(not building.scene_file_path.is_empty())
	DirAccess.remove_absolute("user://city_persistence_test.tscn")
	scene_root.queue_free()
	reopened.queue_free()
	await process_frame
	print("CITY LAYOUT PASS: deterministic seed/type/transform; actual mesh envelopes; gap/street setbacks; owner persistence; no automatic runtime generation; node budget; safe invalid rebuild")
	quit()
