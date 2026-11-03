extends SceneTree
var checks := 0
var failures := 0
func verify(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		push_error(message)
		failures += 1
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	for path in ["res://main.tscn","res://variants/initial.tscn","res://variants/contrast.tscn"]:
		var scene = load(path).instantiate()
		root.add_child(scene)
		scene.set_process(false)
		scene._process(0)
		verify(scene.rig.position.x == 0.0,"start")
		scene.playing=true
		scene._process(12)
		verify(is_equal_approx(scene.rig.position.x,20.0),"halfway")
		scene.playing=false
		scene._process(3)
		verify(is_equal_approx(scene.rig.position.x,20.0),"paused")
		scene.playing=true
		scene._process(1000)
		verify(is_equal_approx(scene.rig.position.x,40.0),"bounded end")
		var e=InputEventKey.new();e.keycode=KEY_R;e.pressed=true
		scene._unhandled_key_input(e);scene._process(0)
		verify(scene.elapsed==0 and not scene.playing and scene.rig.position.x==0,"reset handler")
		verify(scene.find_children("*","MeshInstance3D",true,false).size()==62,"mesh count")
		scene.queue_free()
		await process_frame
	print("%d checks, %d failures; no native rendering assertion" % [checks,failures])
	quit(1 if failures else 0)
