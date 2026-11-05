extends SceneTree
var checks:=0
var failures:=0
func check(value:bool,label:String):
 checks+=1
 print("READER BOARD ","PASS " if value else "FAIL ",label)
 if not value:failures+=1
func _initialize():call_deferred("run")
func key(code:Key):
 var event:=InputEventKey.new()
 event.keycode=code;event.pressed=true
 Input.parse_input_event(event)
 await process_frame
 event=InputEventKey.new();event.keycode=code;event.pressed=false
 Input.parse_input_event(event)
 await process_frame
func run():
 var g=load("res://main.tscn").instantiate()
 root.add_child(g)
 g.set_process(false)
 g.player.set_physics_process(false)
 var p=g.story.panel
 var car=g.neighborhood.car_text
 g.player.position=g.world.anchor("Boarding")
 g.bus.phase="waiting"
 p.open_story(car)
 await process_frame
 check(p.guide_label.text.begins_with("E 다음") and not g.can_board_here(),"waiting bus keeps reader action")
 await key(KEY_E)
 check(p._page==1 and not g.boarded,"real E advances when bus not stopped")
 g.bus.phase="stopped"
 await process_frame
 check(g.can_board_here() and p.guide_label.text.begins_with("E 버스 타기"),"stopped bus replaces last-page close guide")
 g.player.seated=true
 await process_frame
 check(not g.can_board_here() and p.guide_label.text.begins_with("E 닫기"),"seated reader cannot board and retains close guide")
 g.player.seated=false
 g.player.position+=Vector3(4,0,0)
 await process_frame
 check(p.guide_label.text.begins_with("E 닫기"),"leaving boarding radius restores reading")
 g.player.position=g.world.anchor("Boarding")
 g.bus.advance(g.bus.schedule.stop_seconds)
 await process_frame
 check(p.guide_label.text.begins_with("E 닫기"),"departing bus restores reader without closing it")
 g.bus.phase="stopped"
 p.open_story(load("res://config/story_passenger.tres"))
 await process_frame
 check(p.guide_label.text.begins_with("E 버스 타기") and "1 / 2 선택" in p.guide_label.text,"choice and immediate boarding advertised together")
 check(p.guide_label.get_minimum_size().x<=968 and p.guide_label.get_minimum_size().y<=30,"longest boarding/choice guide fits authored label")
 await key(KEY_Q)
 check(not p.is_open and not g.boarded,"Q closes without boarding")
 p.open_story(car)
 await process_frame
 check(p.guide_label.text.begins_with("E 버스 타기"),"open during stop uses current eligibility immediately")
 g.pause_overlay.pause_game()
 var page:int=p._page
 await key(KEY_E)
 check(not paused and not g.boarded and p._page==page,"paused E only resumes, never boards/advances")
 await key(KEY_E)
 check(g.boarded and not p.is_open and g.onboard.active,"next real E boards and closes reader")
 g.restart();g.set_process(false);g.player.set_physics_process(false)
 p.open_story(car)
 await process_frame
 check(not g.boarded and p.guide_label.text.begins_with("E 다음"),"new night clears eligibility without stale prompt")
 g.photo_view()
 check(not g.can_board_here() and p.suspended,"overview excludes boarding context")
 g.leave_photo_view()
 await process_frame
 check(not p.suspended and p.guide_label.text.begins_with("E 다음"),"overview return refreshes existing reader")
 var before:float=g.clock.elapsed
 g._process(.1)
 check(g.clock.elapsed>before and p.is_open,"reading does not freeze shared clock")
 var independent=load("res://scenes/story_panel.tscn").instantiate()
 root.add_child(independent);independent.open_story(car)
 check(independent.guide_label.text.begins_with("E 다음"),"standalone panel works without session dependency")
 independent.free()
 g.app_shutdown.initialize(g,g._prepare_app_shutdown,func():pass)
 g.app_shutdown.request_shutdown()
 while not g.app_shutdown.finished:await process_frame
 g.free();await process_frame
 print("READER BOARDING: %d checks / %d failures"%[checks,failures])
 quit(1 if failures else 0)
