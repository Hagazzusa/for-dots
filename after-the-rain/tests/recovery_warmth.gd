extends SceneTree
## Run serially. Headless checks do not replace actual graphical review.
var failures: Array[String] = []
func check(value: bool, label: String):
	if not value: failures.append(label)
func _initialize(): call_deferred("run")
func run():
	var scene := load("res://scenes/held_drink.tscn") as PackedScene
	var camera := Camera3D.new()
	root.add_child(camera)
	camera.position = Vector3(0, 1.25, 0)
	var a = scene.instantiate()
	var b = scene.instantiate()
	camera.add_child(a)
	camera.add_child(b)
	var ids: Array[int] = []
	var triangles := 0
	for instance in [a,b]:
		for wisp in instance.steam.wisps:
			var id: int = wisp.material_override.get_instance_id()
			check(not ids.has(id), "Material private to each wisp and instance")
			ids.append(id)
			if instance == a: triangles += wisp.mesh.get_faces().size()/3
	check(triangles == 6, "Three billboard quads / six triangles")
	check(not a.visible and not a.steam.visible, "No initial ghost cup/steam")
	a.set_fill(1,true)
	a.set_warmth_context(1,false,false)
	a.present(3,true,-1,false,Vector3.ZERO,0,true,.1,999)
	check(a.visible and a.steam.visible, "Filled warm cup steams when idle")
	check(is_equal_approx(a.steam.elapsed,.1) and b.steam.elapsed == 0, "Local phase, no global time coupling")
	var old_phase: float = a.steam.elapsed
	var old_wisp: Vector3 = a.steam.wisps[1].global_position
	a.present(3,true,-1,false,Vector3.ZERO,0,true,0,10000)
	check(a.steam.elapsed == old_phase and a.steam.wisps[1].global_position.is_equal_approx(old_wisp), "Zero delta freezes CPU steam")
	for phase in [0.0,.5,1.0]:
		a.present(2,true,phase,false,Vector3.ZERO,0,true,.2,0)
		check(not a.steam.visible, "All active sip phases hide steam")
		check(is_equal_approx(a.global_rotation.x,.28+.38*sin(phase*PI)), "Normalized phase controls approved tilt")
	for pitch in [-1.15,0.0,1.15]:
		camera.rotation.x = pitch
		for phase in [-1.0,0.0,.5,1.0]:
			for i in range(10): a.present(3,true,phase,false,Vector3.ZERO,0,true,.1,0)
			check(a.global_position.y >= camera.global_position.y-.43001, "Seated attachment floor is world-space")
			check(a.cup.max_surface_height <= .075001, "Approved liquid stays below rim")
			check(a.cup.min_surface_height >= -.079001, "Approved liquid stays above base")
			for mesh_node in a.get_node("Grip").find_children("*","MeshInstance3D",true,false):
				for vertex in mesh_node.mesh.get_faces():
					check(mesh_node.to_global(vertex).y > .6175, "Seated grip clears bench in extreme views")
	camera.rotation = Vector3.ZERO
	a.present(0,true,-1,false,Vector3.ZERO,0,false,.1,0)
	check(not a.steam.visible, "Empty cup hides steam")
	a.present(3,true,-1,true,Vector3.ZERO,0,false,.1,0)
	check(not a.visible and not a.steam.visible, "Board/photo blocking hides cup and steam")
	a.set_warmth_context(0,false,false)
	a.present(3,true,-1,false,Vector3.ZERO,0,false,.1,0)
	check(not a.steam.visible, "Zero supplied heat hides steam")
	a.set_warmth_context(.18,true,false)
	a.present(3,true,-1,false,Vector3.ZERO,0,false,.1,0)
	check(a.steam.visible, "Sole-owner cooling floor remains visible")
	var rim: Vector3 = a.cup.to_global(Vector3(0,.09,0))
	check(a.steam.global_basis.is_equal_approx(Basis.IDENTITY), "Steam remains gravity-upright")
	for wisp in a.steam.wisps:
		var offset: Vector3 = wisp.global_position-rim
		check(offset.y >= .0549 and offset.y <= .2351, "Steam rises above actual .09 rim")
		check(Vector2(offset.x,offset.z).length() <= .055*.65+.0001, "Shelter limits drift")
	a.set_warmth_context(1,false,true)
	a.present(3,true,-1,false,Vector3.ZERO,0,false,.1,0)
	rim = a.cup.to_global(Vector3(0,.09,0))
	for wisp in a.steam.wisps:
		var offset: Vector3 = wisp.global_position-rim
		check(Vector2(offset.x,offset.z).length() <= .055*.25+.0001, "Umbrella limits drift")
	var grip_meshes := 0
	var grip_triangles := 0
	for mesh_node in a.get_node("Grip").find_children("*","MeshInstance3D",true,false):
		grip_meshes += 1
		var faces: PackedVector3Array = mesh_node.mesh.get_faces()
		grip_triangles += faces.size()/3
		for vertex in faces:
			var p: Vector3 = mesh_node.transform*vertex
			var r := .053+(p.y+.082)/.172*.014
			check(p.y < .04, "Grip stays below cup mouth")
			check(p.y < -.082 or Vector2(p.x,p.z).length() > r+.0003, "Grip outside tapered interior")
	check(grip_meshes == 5 and grip_triangles < 500, "Five simple authored grip meshes below 500 triangles")
	a.reset_visuals()
	check(a.steam.elapsed == 0 and not a.visible and not a.steam.visible, "Reset hides all presentation")
	check(a.previous_walk == Vector2.ZERO and a.cup.target_fill == 0, "Reset clears motion and fill")
	camera.free()
	if failures.is_empty(): print("RECOVERY WARMTH PASS: normalized sip, private steam 6 tris, grip %d tris, extreme seated view, reset/heat" % grip_triangles)
	else:
		for failure in failures.slice(0,15): push_error(failure)
	quit(0 if failures.is_empty() else 1)
