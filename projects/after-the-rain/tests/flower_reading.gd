extends SceneTree
var failures := 0
var checks := 0
func check(ok:bool,label:String):
 checks+=1
 if not ok:
  failures+=1
  push_error(label)
func _initialize():call_deferred("run")
func run():
 var e=load("res://scenes/exploration.tscn").instantiate()
 var panel=load("res://scenes/story_panel.tscn").instantiate()
 root.add_child(e);root.add_child(panel)
 e.initialize(null,panel)
 var a=e.flower_life
 var near_point:Vector3=a.to_global(Vector3(0,0,2))
 var rest:Transform3D=a.work_arm.transform
 var fold:Transform3D=a.paper_fold.transform
 panel.open_story(e.flower_text)
 e.advance(a.dwell_seconds+a.work_seconds*.55,near_point,0)
 check(a.state=="work" and a.work_arm.rotation.z<-.8,"reading does not freeze wrapping gesture")
 e.advance(100,near_point,0)
 check(a.can_wave() and a.elapsed==0,"large step reaches window then preserves it")
 check(a.work_arm.transform.is_equal_approx(rest) and a.paper_fold.transform.is_equal_approx(fold),"window returns wrapping poses to rest")
 panel.close_story()
 e.advance(3,near_point,0)
 check(is_equal_approx(a.elapsed,3),"closed reader consumes existing window")
 for i in range(20):
  panel.open_story(e.flower_text)
  e.advance(50,near_point,0)
  check(a.can_wave() and is_equal_approx(a.elapsed,3),"reopening does not reset or accumulate held time")
  panel.close_story()
 check(a.work_arm.transform.is_equal_approx(rest) and a.paper_fold.transform.is_equal_approx(fold),"repeated reading has no pose drift")
 e.advance(8.5,near_point,0)
 panel.open_story(e.flower_text)
 e.advance(100,near_point,0)
 check(a.can_wave() and is_equal_approx(a.elapsed,11.5),"late reading preserves only remaining half second")
 panel.close_story();e.advance(.6,near_point,0)
 check(a.state=="leave","close resumes original expiry without new greeting window")
 panel.open_story(e.flower_text);e.advance(100,near_point,0)
 check(a.state=="done" and not a.can_wave(),"reading cannot revive completed visit")
 a.reset();e.advance(100,near_point,0)
 check(a.can_wave(),"new visit can wait for reader")
 check(a.request_wave(),"one greeting accepted")
 e.advance(100,near_point,0)
 check(a.state=="done" and a.waved,"reading after greeting never grants second greeting")
 a.reset();e.advance(100,near_point,0)
 e.advance(100,a.to_global(Vector3(0,0,3.3)),0)
 check(a.state=="done","walking beyond notice radius releases hold even with note open")
 a.reset();panel.open_story(load("res://config/story_refuge.tres"))
 e.advance(100,near_point,0)
 check(a.state=="done","another note does not hold flower visit")
 a.reset();panel.open_story(e.flower_text);panel.set_suspended(true)
 e.advance(100,near_point,0)
 check(a.state=="done","hidden reader is not an active flower reading")
 panel.set_suspended(false)
 e.free();panel.free()
 await process_frame
 var g=load("res://main.tscn").instantiate()
 root.add_child(g);current_scene=g
 g.set_process(false)
 g.player.input_enabled=false
 g.player.set_physics_process(false)
 g.player.position=g.exploration.flower_life.to_global(Vector3(0,1.6,2))
 g.story.panel.open_story(g.exploration.flower_text)
 var bus_before:float=g.bus.countdown_seconds()
 var clock_before:float=g.clock.elapsed
 var cat_before:float=g.exploration.cat.phase
 var neighbor_before:float=g.neighborhood.elapsed
 for i in range(25):g._process(1.0)
 check(g.exploration.flower_life.can_wave(),"session holds flower window while reading")
 check(g.clock.elapsed>clock_before+24 and g.bus.countdown_seconds()<bus_before-24,"clock and bus continue while reading flower note")
 check(g.exploration.cat.phase>cat_before and g.neighborhood.elapsed>neighbor_before+24,"cat and car continue independently")
 g.interact();g.interact()
 check(not g.story.panel.is_open and g.exploration.flower_life.can_wave(),"two reader E actions close without stealing greeting")
 g._process(13)
 check(not g.exploration.flower_life.can_wave(),"session closing reader resumes window expiry")
 g.restart()
 check(g.exploration.flower_life.state=="idle" and not g.story.panel.is_open,"session restart clears visit and reader")
 await process_frame
 g.app_shutdown.initialize(g,g._prepare_app_shutdown,func():pass)
 g.app_shutdown.request_shutdown()
 var deadline:int=Time.get_ticks_usec()+3000000
 while not g.app_shutdown.finished and Time.get_ticks_usec()<deadline:await process_frame
 check(g.app_shutdown.finished,"test shutdown releases audio before exit")
 g.free()
 await process_frame
 print("FLOWER READING: %d checks / %d failures"%[checks,failures])
 quit(1 if failures else 0)
