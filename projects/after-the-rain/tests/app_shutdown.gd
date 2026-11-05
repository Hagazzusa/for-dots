extends SceneTree
var failures:=0
var checks:=0
var quit_calls:=0
var completed_calls:=0
var last_timeout:=false
var last_remaining:=0
func check(ok:bool,label:String):
 checks+=1
 if not ok:
  failures+=1
  push_error(label)
func stopped(player)->bool:
 return not is_instance_valid(player) or not player.playing
func _initialize():call_deferred("run")
func record(timed_out:bool,remaining:int):
 completed_calls+=1
 last_timeout=timed_out
 last_remaining=remaining
func wait_finished(controller:Node):
 var deadline=Time.get_ticks_usec()+3000000
 while not controller.finished and Time.get_ticks_usec()<deadline:
  await process_frame
 check(controller.finished,"bounded shutdown completion")
func run():
 var previous_auto=auto_accept_quit
 for case in ["normal","paused","silent"]:
  var paused_case:bool=case=="paused"
  print("SHUTDOWN CASE ",case)
  var game=load("res://main.tscn").instantiate()
  root.add_child(game)
  current_scene=game
  game.player.input_enabled=false
  game.set_process(false)
  var controller=game.app_shutdown
  controller.initialize(game,game._prepare_app_shutdown,func():quit_calls+=1)
  controller.completed.connect(record)
  if case!="silent":
   game.story.radio.toggle()
   game.neighborhood.advance(.01)
  else:
   var released=game.ambience.begin_shutdown()
   var release_deadline=Time.get_ticks_usec()+2000000
   while Time.get_ticks_usec()<release_deadline:
    var alive:=false
    for ref in released:
     if ref.get_ref()!=null:alive=true
    if not alive:break
    await process_frame
   check(game.ambience.begin_shutdown().is_empty(),"owner shutdown is idempotent")
  await process_frame
  check(not controller.is_processing() and not controller.requested,"no ordinary gameplay drain loop")
  check(not auto_accept_quit,"only current scene owns close policy")
  paused=paused_case
  var before_quit=quit_calls
  var before_completed=completed_calls
  root.close_requested.emit()
  var deadline:int=controller._deadline_us
  root.close_requested.emit()
  check(controller.requested and controller._deadline_us==deadline,"duplicate close cannot restart deadline")
  await wait_finished(controller)
  check(quit_calls==before_quit+1 and completed_calls==before_completed+1,"one completion and quit command")
  check(not last_timeout and last_remaining==0,"normal/paused active audio truly releases")
  game.ambience.start();game.ambience.play_chime();game.ambience.footsteps(1,true,false)
  game.story.radio.toggle();game.neighborhood.reset();game.neighborhood.advance(1)
  game.restart()
  check(stopped(game.ambience.rain_player) and stopped(game.ambience.chime_player) and stopped(game.story.radio.player) and stopped(game.neighborhood.heater),"terminal owner commands cannot restart audio")
  check(not game.player.input_enabled and game.process_mode==Node.PROCESS_MODE_DISABLED,"terminal restart cannot reactivate session")
  check(controller._pending.is_empty(),"no weak handles retained after finish")
  paused=false
  game.queue_free()
  await process_frame
  check(auto_accept_quit==previous_auto,"window policy restored when owner freed")
 # Standalone controller: empty audio path and timeout, including zero scaled time.
 for timeout_case in [false,true]:
  var controller=load("res://scripts/app_shutdown.gd").new()
  root.add_child(controller)
  var held=RefCounted.new()
  var refs:Array[WeakRef]=[]
  if timeout_case:refs.append(weakref(held))
  controller.release_timeout_seconds=.05 if timeout_case else NAN
  controller.initialize(root,func():return refs,func():quit_calls+=1)
  controller.completed.connect(record)
  var before=quit_calls
  Engine.time_scale=0.0
  controller.request_shutdown()
  if not timeout_case:check(controller._deadline_us-Time.get_ticks_usec()>1900000 and controller._deadline_us-Time.get_ticks_usec()<=2000000,"nonfinite timeout falls back to bounded default")
  check(not controller.request_shutdown(),"explicit duplicate rejected")
  await wait_finished(controller)
  check(last_timeout==timeout_case and last_remaining==(1 if timeout_case else 0),"honest finite timeout / empty-audio completion")
  check(quit_calls==before+1,"timeout still invokes quit exactly once")
  Engine.time_scale=1.0
  controller.queue_free()
  await process_frame
 check(auto_accept_quit==previous_auto,"non-current scene never takes window policy")
 print("APP SHUTDOWN: %d checks / %d failures"%[checks,failures])
 quit(1 if failures else 0)
