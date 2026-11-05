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
	var ps=load("res://scenes/stories/waiting_passenger.tscn")
	var p=ps.instantiate();var other=ps.instantiate()
	var exchange=load("res://scenes/umbrella_exchange.tscn").instantiate()
	var panel=load("res://scenes/story_panel.tscn").instantiate()
	var reader2=load("res://scenes/story_panel.tscn").instantiate()
	var held=load("res://scenes/held_umbrella.tscn").instantiate()
	var cs=load("res://scenes/onboard_companion.tscn")
	var companion=cs.instantiate();var c2=cs.instantiate()
	for node in [p,other,exchange,panel,reader2,held,companion,c2]:root.add_child(node)
	await process_frame
	var entry:=Vector3(7.5,0,2)
	check((p.head_pivot.get_node("Hood").position+p.head_pivot.position).is_equal_approx(Vector3(0,1.51,-.025)),"authored hood world-relative pose retained")
	check((p.head_pivot.get_node("Face").position+p.head_pivot.position).is_equal_approx(Vector3(0,1.51,.115)),"authored face pose retained")
	check(not (p.state=="boarded" and not p.departed),"early boarding snapshot has no companion without loan")
	p.advance(20.0,"stopped",entry,false)
	check(p.state=="boarded" and not p.departed,"same stopped bus snapshot true without loan")
	p.advance(.1,"departing",entry,false)
	check(p.departed,"departure latched independently of loan")
	p.advance(100.0,"waiting",entry,false)
	check(not (p.state=="boarded" and not p.departed),"later bus cannot create phantom nonloan companion")
	p.leave_with_player()
	check(p.departed,"forced hidden boarding cannot erase departure history")
	p.reset()
	check(not p.departed and p.state=="wait","new evening clears independent departure")
	exchange.initialize(held,p,panel)
	held.borrow();exchange.request_offer();panel.select_choice(0)
	check(not p.thanking and exchange._thanks_pending,"accept defers nod until response closes")
	panel.close_story()
	check(p.thanking and not exchange._thanks_pending,"owned accepted response close starts nod")
	p.advance(.8,"waiting",entry,false)
	check(is_equal_approx(p.head_pivot.rotation.x,.26),"head-only nod peak .26rad")
	check(p.visual.scale==Vector3.ONE and p.scale==Vector3.ONE and other.head_pivot.rotation==Vector3.ZERO,"no body squash or cross-instance nod")
	check(not p.request_thanks(),"duplicate nod request does not restart active gesture")
	panel.story_closed.emit(exchange.offer_text)
	check(is_equal_approx(p.thanks_elapsed,.8),"duplicate close cannot restart gesture")
	p.advance(.8,"waiting",entry,false)
	check(not p.thanking and p.head_pivot.rotation==Vector3.ZERO,"nod settles exactly after1.6s")
	exchange.reset();p.reset();held.borrow();exchange.request_offer();panel.select_choice(1);panel.close_story()
	check(not p.thanking,"decline close never nods")
	exchange.request_offer();panel.close_story()
	check(not p.thanking,"cancel offer never nods")
	exchange.request_offer();panel.select_choice(0)
	var foreign=exchange.offer_text.duplicate()
	panel.open_story(foreign);panel.close_story()
	check(not p.thanking and not exchange._thanks_pending,"foreign resource closure cannot trigger pending thanks")
	exchange.reset();held.borrow();exchange.request_offer();panel.select_choice(0)
	exchange.reset()
	check(not p.thanking and not panel.is_open,"reset clears pending before owned close")
	held.borrow();exchange.request_offer();panel.select_choice(0)
	exchange.initialize(held,p,reader2)
	panel.close_story()
	check(not p.thanking and not exchange._thanks_pending,"rebind invalidates pending old reader closure")
	exchange.reset();exchange.initialize(held,p,panel);held.borrow();exchange.request_offer();panel.select_choice(0)
	p.state="walk";panel.close_story()
	check(not p.thanking,"departing person cannot nod on late response close")
	exchange.reset();p.reset();held.borrow();exchange.request_offer();panel.select_choice(0)
	p.advance(p.door_open_delay-0.01,"stopped",entry,false)
	panel.close_story()
	check(p.thanking,"accepted response just before walking starts stationary nod")
	p.advance(0.02,"stopped",entry,false)
	check(p.state=="walk" and not p.thanking and p.head_pivot.rotation==Vector3.ZERO,"walking transition cancels nod without delaying path")
	p.reset();p.request_thanks();p.leave_with_player()
	check(not p.thanking and p.head_pivot.rotation==Vector3.ZERO,"boarding cancels nod")
	p.reset();p.request_thanks();p.advance(100000.0,"waiting",entry,false)
	check(not p.thanking and p.head_pivot.rotation==Vector3.ZERO,"huge explicit nod delta settles safely")
	check(not companion.visible and not companion.companion_present,"companion defaults absent")
	companion.configure(false,true)
	check(not companion.visible and not companion.has_loan and not companion.umbrella.visible,"loan alone never creates occupant")
	companion.configure(true,false)
	check(companion.visible and not companion.umbrella.visible,"actual nonloan companion shows bag and sleeve only")
	companion.configure(true,true)
	check(companion.visible and companion.umbrella.visible and not c2.visible,"actual loan companion includes folded item with instance isolation")
	var meshes=companion.find_children("*","MeshInstance3D",true,false)
	var triangles:=0
	var bounds_ok:=true
	for mesh in meshes:
		var faces:PackedVector3Array=mesh.mesh.get_faces()
		triangles+=faces.size()/3
		for vertex in faces:
			var point:Vector3=mesh.global_transform*vertex
			bounds_ok=bounds_ok and point.x>.42 and point.x<.78 and point.y>1.07 and point.y<1.55 and point.z>-.82 and point.z<-.59
	check(meshes.size()==9 and triangles<=300,"saved9-mesh companion within300 triangles")
	check(bounds_ok,"reduced peripheral companion remains in front of frame, x>.42 and top<1.55")
	check(companion.scale.is_equal_approx(Vector3(.72,.72,.72)),"uniform shrink preserves prop proportions")
	check(companion.get_node("PaperBag").global_position.is_equal_approx(Vector3(.5096,1.18,-.72)),"smaller bag lower-right authored anchor")
	# Lower-right silhouette must not grow back into the central view: compare
	# analytic projected X extent at the actual default seat-camera height.
	var projected_min:=INF
	var projected_max:=-INF
	for mesh in meshes:
		for vertex in mesh.mesh.get_faces():
			var point:Vector3=mesh.global_transform*vertex-Vector3(0,1.7,0)
			projected_min=minf(projected_min,point.x/-point.z)
			projected_max=maxf(projected_max,point.x/-point.z)
	check(projected_min>.51 and projected_max-projected_min<.61,"projected silhouette stays peripheral and bounded at default camera")
	check(companion.find_children("*","Light3D",true,false).is_empty() and companion.find_children("*","CollisionObject3D",true,false).is_empty(),"no extra light or collision")
	companion.reset()
	check(not companion.visible and not companion.has_loan,"reset clears all companion presentation")
	for node in [p,companion]:
		node.reset()
		var packed:=PackedScene.new()
		var path:String="user://continuity_"+node.name+".tscn"
		check(packed.pack(node)==OK and ResourceSaver.save(packed,path)==OK,"authored component saves")
		var restored=ResourceLoader.load(path,"",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
		root.add_child(restored)
		check(restored.has_node("Visual/HeadPivot") if restored.has_node("Visual") else restored.has_node("FoldedUmbrella"),"saved pivots and prop hierarchy reopen")
		restored.free();DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	for node in [exchange,p,other,panel,reader2,held,companion,c2]:node.free()
	await process_frame
	print("RECOVERY PASSENGER CONTINUITY: %d checks / %d failures"%[checks,failures])
	quit(1 if failures else 0)
