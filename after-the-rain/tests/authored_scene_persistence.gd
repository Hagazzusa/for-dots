extends SceneTree
## Standalone, real PackedScene persistence and route-instance test. No production edits.
var arrival_count := 0
func _initialize():
	call_deferred("run")
func arrived():
	arrival_count += 1
func fingerprint(node: Node, root_node: Node, result: Array):
	var row = [str(root_node.get_path_to(node)),node.get_class(),node.scene_file_path if node != root_node else "<root>"]
	if node != root_node:
		assert(node.owner != null, "Unowned authored node: " + str(root_node.get_path_to(node)))
		assert(node.owner.is_ancestor_of(node), "Owner is not ancestor")
	if node is Node3D:
		row.append(node.transform)
	if node is MeshInstance3D:
		assert(node.mesh != null)
		row.append(node.mesh.get_class())
		row.append(node.mesh.get_surface_count())
		row.append(node.mesh.get_aabb())
	if node is CollisionShape3D:
		assert(node.shape != null)
		row.append(node.shape.get_class())
	result.append(row)
	for child in node.get_children():
		fingerprint(child,root_node,result)
func persistence(path: String, shelter_path: String):
	var source = load(path).instantiate()
	var original: Array = []
	fingerprint(source,source,original)
	var glb = source.get_node(shelter_path)
	assert(glb.scene_file_path == "res://assets/shelter.glb")
	assert(glb.find_children("*","MeshInstance3D",true,false).size() > 0)
	var packed = PackedScene.new()
	assert(packed.pack(source) == OK)
	var destination = "user://persistence_" + path.get_file()
	assert(ResourceSaver.save(packed,destination) == OK)
	source.free()
	var reloaded = ResourceLoader.load(destination,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	var reopened: Array = []
	fingerprint(reloaded,reloaded,reopened)
	assert(original == reopened, "Saved/reopened hierarchy or GLB geometry changed: " + path)
	assert(reloaded.get_node(shelter_path).scene_file_path == "res://assets/shelter.glb")
	print("ROUNDTRIP PASS ",path," / nodes ",reopened.size())
	reloaded.free()
	DirAccess.remove_absolute(destination)
func run():
	var orphan_before = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	persistence("res://scenes/bus_stop.tscn","ShelterAsset")
	persistence("res://scenes/world.tscn","BusStop/ShelterAsset")
	assert(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT) == orphan_before)
	var scene = load("res://scenes/night_bus.tscn")
	var a = scene.instantiate()
	var b = scene.instantiate()
	root.add_child(a)
	root.add_child(b)
	a.arrived.connect(arrived)
	var a_left = a.get_node("Visual/Doors/Left")
	var b_left = b.get_node("Visual/Doors/Left")
	var b_closed = b_left.position
	var a_mesh = a_left.get_child(0)
	var b_mesh = b_left.get_child(0)
	# Full opacity intentionally restores authored immutable materials. Waiting now
	# uses private fade copies; that distinct behavior is covered by recovery_bus_visibility.
	a.visual.set_route_opacity(1.0)
	b.visual.set_route_opacity(1.0)
	var original_color = b_mesh.material_override.albedo_color
	# Static bus materials intentionally share immutable resources. Door motion must not mutate them.
	assert(a_mesh.material_override == b_mesh.material_override)
	a.advance(a.schedule.wait_seconds)
	a.advance(a.schedule.approach_seconds)
	assert(a.phase == "stopped" and a.visual.door_open)
	assert(b.phase == "waiting" and not b.visual.door_open)
	assert(arrival_count == 1)
	await create_timer(a.visual.door_duration + .1).timeout
	assert(is_equal_approx(a_left.position.x, a.visual.OPEN_X[0]))
	assert(is_equal_approx(a_left.position.z, a.visual.POCKET_Z[0]))
	assert(b_left.position == b_closed)
	assert(b_mesh.material_override.albedo_color == original_color)
	# A node-local material replacement also leaves the other instance untouched.
	a_mesh.material_override = a_mesh.material_override.duplicate()
	a_mesh.material_override.albedo_color = Color.MAGENTA
	assert(b_mesh.material_override.albedo_color == original_color)
	a.reset()
	await create_timer(a.visual.door_duration + .1).timeout
	assert(a_left.position == b_closed and not a.visual.door_open)
	assert(b.phase == "waiting" and b.phase_time == 0 and arrival_count == 1)
	var bus_count = AudioServer.bus_count
	for cycle in range(3):
		var audio_a = load("res://scenes/ambience.tscn").instantiate()
		var audio_b = load("res://scenes/ambience.tscn").instantiate()
		root.add_child(audio_a)
		root.add_child(audio_b)
		assert(AudioServer.bus_count == bus_count)
		assert(audio_a.rain_filter == audio_b.rain_filter)
		audio_a.advance(1,true,false,"stopped")
		assert(audio_a.rain_player.volume_db == -18 and audio_b.rain_player.volume_db == -11)
		audio_a.queue_free()
		audio_b.queue_free()
		await process_frame
	assert(AudioServer.bus_count == bus_count)
	a.queue_free()
	b.queue_free()
	await process_frame
	await process_frame
	assert(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT) == orphan_before)
	print("AUTHORED SCENE PASS: world/shelter save-reopen with GLB intact; no orphan nodes; real bus door tween/state isolation; immutable shared materials; fixed audio bus count")
	quit()
