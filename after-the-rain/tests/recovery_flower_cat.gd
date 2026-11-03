extends SceneTree
var failures:=0
var checks:=0
var waves:=0
var greetings:=0
func check(ok:bool,label:String)->void:
	checks+=1
	if not ok:
		failures+=1
		push_error(label)
func _initialize()->void:call_deferred("run")
func run()->void:
	var fs=load("res://scenes/flower_life.tscn")
	var cs=load("res://scenes/rain_cat.tscn")
	var f=fs.instantiate();var f2=fs.instantiate()
	var cat=cs.instantiate();var cat2=cs.instantiate()
	for node in [f,f2,cat,cat2]:root.add_child(node)
	await process_frame
	f.caption_requested.connect(func(_text:String):waves+=1)
	cat.caption_requested.connect(func(_text:String):greetings+=1)
	for node in [f,cat]:
		check(node.visual.find_children("*","MeshInstance3D",true,false).size()==14,"bounded authored 14-mesh %s"%node.name)
		check(node.find_children("*","Light3D",true,false).is_empty() and node.find_children("*","CollisionObject3D",true,false).is_empty(),"no extra lights/collisions %s"%node.name)
	check(f.has_node("Interaction") and cat.has_node("Interaction"),"root aim anchors exist")
	check(f._materials[0]!=f2._materials[0],"private flower opacity resources")
	f.advance(10.0,Vector3(6,0,0))
	check(f.state=="idle" and not f.visual.visible,"distant player does not start event")
	f.advance(1.0,Vector3(0,1,2))
	check(f.state=="dwell" and not f.can_wave(),"proximity dwell before any event")
	f.advance(0.1,Vector3(6,0,0))
	check(f.state=="idle","walking away cancels incomplete dwell")
	f.advance(5.0,Vector3(0,1,2))
	check(f.state=="window" and f.can_wave(),"dwell plus work enters optional 12s window")
	check(f.request_wave() and not f.request_wave() and waves==1,"explicit wave accepted once")
	f.advance(1.25,Vector3(0,1,2))
	check(absf(f.arm.rotation.z)>0.5 and f.visual.scale==Vector3.ONE,"saved arm pivots without body squash")
	check(f2.state=="idle" and not f2.waved,"flower instance isolation")
	f.advance(10.0,Vector3(0,1,2))
	check(f.state=="done" and not f.visual.visible,"wave finishes and leaves")
	f.advance(99.0,Vector3(0,1,2))
	check(f.state=="done" and waves==1 and f.pickup.active,"lingering starts only the new pickup, never replays greeting")
	f.advance(f.pickup.duration(),Vector3(0,1,2))
	check(f.pickup.completed and not f.pickup.active,"new one-time pickup finishes before return visit")
	f.advance(0.0,Vector3(4.3,0,0))
	check(f.state=="idle" and not f.waved,"walking out rearms optional visit")
	f.advance(f.dwell_seconds+f.window_seconds+.2,Vector3(0,1,2))
	check(f.state=="leave" and waves==1,"missed wave window safely leaves")
	f.advance(1.8,Vector3(0,1,2))
	check(f.state=="done","missed event completes")
	f.reset();f.advance(1e12,Vector3(0,0,2))
	check(f.state=="done","huge flower delta bounded")
	f.reset();f.advance(NAN,Vector3.ZERO)
	check(f.state=="idle","nonfinite flower delta ignored")
	cat.advance(3.0,0.5)
	check(cat.emergence==0.0,"cat waits for genuine lull")
	cat.advance(1.4,1.0)
	check(is_equal_approx(cat.emergence,0.5) and not cat.can_greet(),"cat emerges halfway in1.4s")
	cat.advance(1.4,0.5)
	check(cat.can_greet(),"hysteresis retains emergence target")
	check(cat.request_greeting() and not cat.request_greeting() and greetings==1,"one optional greeting per emergence")
	cat.advance(1.2,1.0)
	check(is_equal_approx(cat.eyes.scale.y,0.08) and cat.visual.scale==Vector3.ONE,"slow blink affects only eyes")
	check(cat2.emergence==0.0 and not cat2.greeted,"cat instance isolation")
	cat.advance(1.2,1.0)
	check(cat.eyes.scale.y==1.0 and not cat.greeting_active and not cat.can_greet(),"blink finishes without repeated greeting")
	cat.advance(2.8,0.0)
	check(cat.emergence==0.0 and not cat.greeted,"rain returns cat to rest and rearms")
	cat.advance(2.8,1.0)
	check(cat.can_greet(),"next lull may greet again")
	check(cat.get_node("Interaction").position.is_equal_approx(cat.visual.position+Vector3(0,.27,.18)),"interaction tracks moving head")
	# Geometry checks use actual authored meshes throughout motion, not docs alone.
	var cat_bounds_ok:=true
	for step in range(101):
		cat.reset();cat.advance(2.8*float(step)/100.0,1.0)
		for mesh in cat.visual.find_children("*","MeshInstance3D",true,false):
			for vertex in mesh.mesh.get_faces():
				var point:Vector3=mesh.global_transform*vertex
				cat_bounds_ok=cat_bounds_ok and point.y>=.0999 and point.y<.55 and point.z>0.0 and point.z<.88
	check(cat_bounds_ok,"all intermediate cat surfaces stay below sill above pavement inside awning/facade")
	var flower_bounds_ok:=true
	f.reset();f.advance(5.0,Vector3(0,0,2));f.request_wave()
	for step in range(101):
		f.advance(.025,Vector3(0,0,2))
		for mesh in f.visual.find_children("*","MeshInstance3D",true,false):
			for vertex in mesh.mesh.get_faces():
				var point:Vector3=mesh.global_transform*vertex
				flower_bounds_ok=flower_bounds_ok and point.z>.0325 and point.z<.14 and point.y<2.3025 and point.x> -1.5275 and point.x<.7675
	check(flower_bounds_ok,"whole wave silhouette remains in front of opaque backdrop inside actual window frame")
	var before:float=cat.phase
	paused=true
	await create_timer(.03,true).timeout
	check(cat.phase==before,"explicit-only animation freezes without updates")
	paused=false
	for node in [f,cat]:
		node.reset()
		var packed:=PackedScene.new()
		var path:String="user://recovery_"+node.name+".tscn"
		check(packed.pack(node)==OK and ResourceSaver.save(packed,path)==OK,"save authored %s"%node.name)
		var reopened=ResourceLoader.load(path,"",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
		root.add_child(reopened)
		check(reopened.has_node("Interaction") and reopened.visual.find_children("*","MeshInstance3D",true,false).size()==14,"reopen all saved mesh and aim nodes")
		reopened.free();DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	for node in [f,f2,cat,cat2]:node.free()
	await process_frame
	print("RECOVERY FLOWER CAT: %d checks / %d failures"%[checks,failures])
	quit(1 if failures else 0)
