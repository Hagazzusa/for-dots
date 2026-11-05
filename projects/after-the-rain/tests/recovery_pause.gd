extends SceneTree
var failures := 0
var checks := 0
var restarts := 0
var mutes := 0
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		push_error(label)
func key(code: int) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
	var released := InputEventKey.new()
	released.keycode = code
	released.pressed = false
	Input.parse_input_event(released)
	await process_frame
func settle() -> void:
	await process_frame
	await process_frame
	await process_frame
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var scene = load("res://scenes/pause_overlay.tscn")
	var a = scene.instantiate()
	var b = scene.instantiate()
	root.add_child(a)
	root.add_child(b)
	a.restart_requested.connect(func():restarts+=1)
	a.mute_requested.connect(func():mutes+=1)
	await settle()
	check(a.process_mode==Node.PROCESS_MODE_ALWAYS,"only overlay processes while paused")
	check(not a.active and not a.panel.visible and a.hint.visible,"initial inactive")
	paused=true
	check(not a.pause_game() and not a._owns_pause,"cannot claim external pause")
	a.reset()
	check(paused,"nonowner reset preserves external pause")
	paused=false
	check(a.pause_game() and paused,"explicit pause acquires ownership")
	check(not b.pause_game(),"second instance cannot steal pause")
	b.free()
	check(paused and a.active,"free nonowner preserves owner pause")
	var timer := Timer.new()
	timer.process_mode=Node.PROCESS_MODE_PAUSABLE
	timer.wait_time=0.2
	timer.one_shot=true
	root.add_child(timer)
	timer.start()
	var before:=timer.time_left
	await create_timer(0.04,true).timeout
	check(is_equal_approx(before,timer.time_left),"gameplay timer frozen")
	await key(KEY_M)
	check(mutes==1 and paused,"mute stays paused and emits once")
	await key(KEY_E)
	check(not paused and not a.active,"real E input resumes")
	await key(KEY_SPACE)
	check(paused and a.active,"real Space opens")
	await key(KEY_R)
	check(not paused and restarts==1,"R releases then restarts once")
	await key(KEY_R)
	check(restarts==1,"inactive R is not duplicated")
	a.pause_game()
	await settle()
	check(root.gui_get_focus_owner()==a.resume_button,"resume initially keyboard focused")
	await key(KEY_TAB)
	await settle()
	check(root.gui_get_focus_owner()==a.restart_button,"Tab reaches restart")
	await key(KEY_ENTER)
	await settle()
	check(restarts==2 and not paused,"Enter activates focused button")
	var original_size:=root.size
	var original_scale:=root.content_scale_size
	var original_mode:=root.content_scale_mode
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size=Vector2i(1280,720)
	for dimensions in [Vector2i(1180,812),Vector2i(960,540),Vector2i(638,358),Vector2i(480,270),Vector2i(478,718)]:
		root.size=dimensions
		a.pause_game()
		a._queue_layout()
		await settle()
		var bounds:Rect2=a.panel.get_global_rect()
		var viewport_bounds:=root.get_visible_rect()
		check(viewport_bounds.encloses(bounds),"panel within viewport %s"%dimensions)
		var scale_factor:=root.get_stretch_transform().get_scale().abs().y
		check(a.content.get_node("Guide").get_theme_font_size("font_size")*scale_factor>=13.99,"physical body font floor %s"%dimensions)
		check(a.scroll.get_global_rect().intersection(a.resume_button.get_global_rect()).size.y>=a.resume_button.size.y-1.0,"focused Resume visible after resize %s"%dimensions)
		if dimensions==Vector2i(1180,812):
			check(a.scroll.scroll_vertical==0,"normal window heading not scrolled off")
		a.restart_button.grab_focus()
		a._queue_layout()
		await settle()
		check(a.scroll.get_global_rect().intersection(a.restart_button.get_global_rect()).size.y>=a.restart_button.size.y-1.0,"focused Restart visible %s"%dimensions)
		await key(KEY_HOME)
		a._queue_layout()
		await settle()
		check(a.scroll.scroll_vertical==0,"Home reading not overridden by focus reveal")
		a.resume_button.grab_focus()
		await settle()
		await key(KEY_HOME)
		await key(KEY_TAB)
		await settle()
		check(root.gui_get_focus_owner()==a.restart_button,"Home then Tab focuses Restart %s"%dimensions)
		check(a.scroll.get_global_rect().intersection(a.restart_button.get_global_rect()).size.y>=a.restart_button.size.y-1.0,"Home then Tab reveals focused Restart %s"%dimensions)
		await key(KEY_END)
		check(a.scroll.scroll_vertical>=0,"End scroll valid")
		a.resume_game()
	root.size=original_size
	root.content_scale_size=original_scale
	root.content_scale_mode=original_mode
	await settle()
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
	a.pause_game();a.resume_game()
	check(Input.mouse_mode==Input.MOUSE_MODE_VISIBLE,"visible cursor restored")
	var packed:=PackedScene.new()
	check(packed.pack(a)==OK and ResourceSaver.save(packed,"user://pause_roundtrip.tscn")==OK,"saved hierarchy pack/save")
	var reopened=ResourceLoader.load("user://pause_roundtrip.tscn","",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	root.add_child(reopened)
	await settle()
	check(reopened.process_mode==Node.PROCESS_MODE_ALWAYS and reopened.has_node("Root/Panel/Padding/Scroll/Content/Resume") and not reopened.active,"reopen saved controls inactive")
	check(reopened.resume_button.get_theme_font("font").resource_path.contains("NotoSansCJK"),"real Korean font inherited")
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://pause_roundtrip.tscn"))
	reopened.free()
	a.pause_game()
	a.free()
	check(not paused,"free owner releases owned pause")
	timer.free()
	await settle()
	print("RECOVERY PAUSE: %d checks / %d failures"%[checks,failures])
	quit(1 if failures else 0)
