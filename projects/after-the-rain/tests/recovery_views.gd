extends SceneTree
var failures:=0
var checks:=0
var finishes:=0
func check(ok:bool,label:String)->void:
	checks+=1
	if not ok:
		failures+=1
		push_error(label)
func _initialize()->void:call_deferred("run")
func run()->void:
	var ride_scene=load("res://scenes/onboard_view.tscn")
	var overview_scene=load("res://scenes/overview_view.tscn")
	var a=ride_scene.instantiate();var b=ride_scene.instantiate()
	var authored:=Transform3D(Basis.from_euler(Vector3(.1,.2,.03)),Vector3(.23,2.13,-.4))
	a.get_node("Camera3D").transform=authored
	a.position=Vector3(8,1,-3)
	var rest:Transform3D=a.transform
	root.add_child(a);root.add_child(b)
	await process_frame
	a.finished.connect(func():finishes+=1)
	check(a.camera.transform.is_equal_approx(authored),"ready preserves variant authored camera full transform")
	check(not a.start_linger(),"cannot linger before completed ride")
	a.begin();a.advance(4.0)
	check(a.position.is_equal_approx(rest.origin+Vector3(.75,0,0)),"default8s3m easing preserved")
	check(a.camera.basis.is_equal_approx(authored.basis) and absf(a.camera.position.y-authored.origin.y)<=a.ride_sway+.00001,"ride sway relative to authored pose")
	check(b.elapsed==0.0 and b.camera.position.is_equal_approx(Vector3(0,1.7,0)),"second ride isolated")
	a.advance(4.0);a.advance(100.0)
	check(finishes==1 and not a.active and not a.linger,"default ending unchanged and once")
	check(a.position.is_equal_approx(rest.origin+a.travel),"ride endpoint exactly3m")
	check(a.start_linger() and not a.start_linger(),"explicit linger only once after finish")
	var bounded:=true
	for i in range(10000):
		a.advance(.13)
		bounded=bounded and a.position.is_equal_approx(rest.origin+a.travel) and a.camera.position.distance_to(authored.origin)<=.002101 and a.linger_phase>=0.0 and a.linger_phase<TAU and a.camera.basis.is_equal_approx(authored.basis)
	check(bounded,"10000 linger updates bound camera to2.1mm with no world drift or rotation loss")
	check(finishes==1 and a.elapsed==8.0,"linger never replays completion or ages completed ride")
	a.advance(1e12)
	check(is_finite(a.linger_phase) and a.camera.position.distance_to(authored.origin)<=.002101,"huge linger delta remains bounded")
	var phase:float=a.linger_phase
	a.advance(NAN);a.advance(-2.0)
	check(a.linger_phase==phase,"nonfinite and negative input do not advance linger")
	a.stop_linger();a.stop_linger()
	check(not a.linger and a.camera.transform.is_equal_approx(authored) and finishes==1,"stop restores exact authored camera without callbacks")
	a.reset()
	check(a.transform.is_equal_approx(rest) and a.camera.transform.is_equal_approx(authored) and not a.visible and not a.linger and a.linger_phase==0.0,"reset restores full authored pose and transient state")
	a.begin();a.advance(8.0)
	check(finishes==2,"replay completion once per evening")
	a.reset()
	var player_camera:=Camera3D.new()
	player_camera.position=Vector3(1,2,3)
	root.add_child(player_camera)
	player_camera.make_current()
	var original:=player_camera.transform
	var v=overview_scene.instantiate();var v2=overview_scene.instantiate()
	root.add_child(v);root.add_child(v2)
	check(v.camera!=v2.camera,"overview cameras instance local")
	var direction:Vector3=(Vector3(0,1.2,0)-v.camera.global_position).normalized()
	check((-v.camera.global_basis.z).dot(direction)>.99999,"saved overview aims at approved target")
	check(v.begin() and not v.begin() and v.camera.current,"overview activates own camera idempotently")
	check(player_camera.transform==original and not v2.active,"overview never changes body camera transform or other instance")
	v.end()
	check(player_camera.current and not v.active,"ending overview restores previous camera")
	v.begin();v2.begin();v.end()
	check(v2.camera.current,"noncurrent overview does not steal later camera")
	v2.end()
	v.reset();player_camera.make_current()
	v.begin();v.reset()
	check(player_camera.current and not v.active,"reset releases owned overview")
	var saved:=PackedScene.new()
	check(saved.pack(v)==OK and ResourceSaver.save(saved,"user://overview_roundtrip.tscn")==OK,"overview saved hierarchy packs")
	var reopened=ResourceLoader.load("user://overview_roundtrip.tscn","",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	root.add_child(reopened)
	check(not reopened.active and reopened.camera.position.is_equal_approx(Vector3(5.5,2.7,10)),"reopen retains camera configuration not session state")
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://overview_roundtrip.tscn"))
	for node in [a,b,v,v2,reopened,player_camera]:node.free()
	await process_frame
	print("RECOVERY VIEWS: %d checks / %d failures"%[checks,failures])
	quit(1 if failures else 0)
