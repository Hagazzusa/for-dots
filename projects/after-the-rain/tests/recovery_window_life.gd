extends SceneTree
var failures:=0
var checks:=0
func check(ok:bool,label:String)->void:
	checks+=1
	if not ok:
		failures+=1
		push_error(label)
func _initialize()->void:call_deferred("run")
func run()->void:
	var scene=load("res://scenes/window_life.tscn")
	var a=scene.instantiate();var b=scene.instantiate()
	root.add_child(a);root.add_child(b)
	await process_frame
	check(a.get_child_count()==1 and a.pane.mesh.get_faces().size()==6,"one authored quad two triangles")
	check(a.find_children("*","Light3D",true,false).is_empty() and a.find_children("*","CollisionObject3D",true,false).is_empty(),"no light or collision")
	check(a.material!=b.material and a.material==a.pane.material_override,"per-instance active material")
	for pair in [[0.0,0.0],[12.0,0.0],[15.0,.5],[18.0,1.0],[72.0,1.0],[75.0,.5],[78.0,0.0],[159.0,0.0]]:
		a.present(pair[0]);check(is_equal_approx(a.lamp_strength,pair[1]),"lamp schedule %s"%pair[0])
	a.present(42.5)
	check(is_equal_approx(a.silhouette_progress,.5) and is_equal_approx(a.silhouette_strength,1.0),"crossing midpoint only during lit interval")
	check(b.phase==0.0 and not b.pane.visible and b.material.get_shader_parameter("lamp_strength")==0.0,"second instance unaffected")
	var strength:float=a.lamp_strength
	var silhouette:float=a.silhouette_progress
	b.cycle_seconds=80.0
	b.lamp_on_start=8.0
	b.lamp_on_fade=4.0
	b.present(10.0)
	check(is_equal_approx(b.lamp_strength,.5) and a.cycle_seconds==160.0,"Inspector timing variation stays instance local")
	a.present(202.5)
	check(is_equal_approx(a.phase,42.5) and a.lamp_strength==strength and a.silhouette_progress==silhouette,"160s deterministic period")
	a.present(NAN);a.present(INF)
	check(is_equal_approx(a.phase,42.5),"nonfinite input ignored")
	a.present(-10.0)
	check(a.phase==0.0 and not a.pane.visible,"negative time clamps to beginning")
	a.present(1e12)
	check(a.phase>=0.0 and a.phase<a.cycle_seconds,"huge elapsed bounded")
	var bounded:=true
	for step in range(1601):
		a.present(float(step)*.1)
		bounded=bounded and a.lamp_strength>=0.0 and a.lamp_strength<=1.0 and a.silhouette_strength>=0.0 and a.silhouette_strength<=1.0
	check(bounded,"whole cycle levels remain normalized")
	a.present(42.5)
	paused=true
	await create_timer(.03,true).timeout
	check(is_equal_approx(a.phase,42.5),"no autonomous clock during pause")
	paused=false
	a.reset()
	check(a.phase==0.0 and a.lamp_strength==0.0 and not a.pane.visible,"reset restores dark pane")
	# Actual source geometry: named saved Across_04 transform + imported Apartment_B.
	var layout=load("res://scenes/city_layout.tscn").get_state()
	var placement:=Transform3D.IDENTITY
	var found:=false
	for n in range(layout.get_node_count()):
		if str(layout.get_node_path(n)).trim_prefix("./")!="Generated/Across_04":continue
		for prop in range(layout.get_node_property_count(n)):
			if layout.get_node_property_name(n,prop)=="transform":
				placement=layout.get_node_property_value(n,prop);found=true
	var model=load("res://assets/city/apartment_b.glb").instantiate()
	root.add_child(model)
	var meshes=model.find_children("*","MeshInstance3D",true,false)
	if model is MeshInstance3D:meshes.append(model)
	var points:PackedVector3Array=[]
	for node in meshes:
		for surface in range(node.mesh.get_surface_count()):
			var material:Material=node.mesh.surface_get_material(surface)
			if material==null or not "Unlit opaque blue window" in material.resource_name:continue
			var arrays:Array=node.mesh.surface_get_arrays(surface)
			for vertex in arrays[Mesh.ARRAY_VERTEX]:
				if vertex.x> -1.7 and vertex.x<-.4 and vertex.y>3.4 and vertex.y<5.2 and vertex.z>-.2:
					points.append(placement*node.global_transform*vertex)
	check(found and points.size()>10,"target glass verified from actual imported mesh/material and city placement")
	if not points.is_empty():
		var glass_bounds:=AABB(points[0],Vector3.ZERO)
		for point in points:glass_bounds=glass_bounds.expand(point)
		var pane_bounds:AABB=a.pane.global_transform*a.pane.get_aabb()
		check(pane_bounds.position.x>glass_bounds.position.x and pane_bounds.end.x<glass_bounds.end.x and pane_bounds.position.y>glass_bounds.position.y and pane_bounds.end.y<glass_bounds.end.y,"quad fits strictly inside measured glass envelope")
		check(glass_bounds.position.z-a.global_position.z>0.003 and glass_bounds.position.z-a.global_position.z<0.006,"quad 3–6mm in front of nearest glass surface")
	check(not FileAccess.get_file_as_string("res://shaders/window_life.gdshader").contains("TIME"),"shader has no engine time")
	var saved:=PackedScene.new()
	check(saved.pack(a)==OK and ResourceSaver.save(saved,"user://window_life_qa.tscn")==OK,"authored window saves")
	var reopened=ResourceLoader.load("user://window_life_qa.tscn","",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	root.add_child(reopened)
	check(reopened.has_node("Pane") and reopened.material!=a.material and reopened.phase==0.0,"reopen private material and dark reset")
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://window_life_qa.tscn"))
	for node in [a,b,reopened,model]:node.free()
	await process_frame
	print("RECOVERY WINDOW LIFE: %d checks / %d failures"%[checks,failures])
	quit(1 if failures else 0)
