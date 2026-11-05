extends SceneTree
func _initialize():call_deferred("run")
func run():
 var g=load("res://main.tscn").instantiate();root.add_child(g)
 g.set_process(false);g.player.set_physics_process(false);g.player.input_enabled=false
 g.restart();g._process(.25)
 assert(is_equal_approx(g.rain_details.elapsed,.25))
 assert(g.rain_details.lull==g.weather.strength)
 g.player.sit(g.world.anchor("Seat"));g.wait_quietly()
 var display_time=g.clock.elapsed
 assert(display_time>60 and is_equal_approx(g.time,.25))
 g._process(0)
 assert(is_equal_approx(g.rain_details.elapsed,.25))
 assert(is_equal_approx(g.window_life.phase,fposmod(display_time,160.0)))
 g.set_process(true)
 g.pause_overlay.pause_game()
 var drop=g.rain_details.get_drop_position(0)
 await create_timer(.1,true).timeout
 assert(g.rain_details.get_drop_position(0)==drop)
 g.pause_overlay.resume_game()
 g.set_process(false)
 g.player.stand(g.world.anchor("Boarding"));g.bus.advance(g.bus.schedule.approach_seconds)
 g.board_bus();g.onboard.advance(9);assert(g.ride_finished)
 g.interact();assert(g.onboard.linger)
 var clock_before=g.clock.elapsed;var rain_before=g.rain_details.elapsed
 g._process(.2)
 assert(g.clock.elapsed==clock_before)
 assert(is_equal_approx(g.rain_details.elapsed,rain_before+.2))
 g.restart()
 assert(g.time==0 and g.clock.elapsed==0 and g.rain_details.elapsed==0)
 assert(g.window_life.phase==0 and g.rain_details.lull==0)
 for n in g.find_children("*","",true,false):
  if n is AudioStreamPlayer or n is AudioStreamPlayer3D:n.stop();n.stream=null
 await create_timer(.2).timeout
 g.free();await create_timer(.3).timeout
 print("ATMOSPHERE INTEGRATION PASS: explicit evening/presentation clocks, quiet-wait, pause, linger, reset")
 quit()
