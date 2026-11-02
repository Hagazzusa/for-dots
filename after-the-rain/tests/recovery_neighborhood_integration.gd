extends SceneTree
func _initialize():call_deferred("run")
func run():
 var game=load("res://main.tscn").instantiate()
 root.add_child(game)
 game.set_process(false);game.player.set_physics_process(false);game.player.input_enabled=false
 game.restart()
 var bounds=game.exploration.rain_cover.get_world_bounds()
 assert(bounds.position.is_equal_approx(Vector3(-10.825,0,-6.12)))
 assert(bounds.size.is_equal_approx(Vector3(3.65,2.605,1)))
 assert(game.world.additional_shelters==game.rain.additional_shelters)
 assert(game.world.is_sheltered(Vector3(-9,1.65,-5.6)))
 assert(not game.world.is_sheltered(Vector3(-9,1.65,-5.05)))
 assert(game.exploration.flower.position.is_equal_approx(Vector3(1.25,1.76,.12)))
 game.clock.advance(57)
 game._process(0)
 assert(is_equal_approx(game.weather.strength,1.0))
 assert(game.rain.instances.multimesh.visible_instance_count==812)
 game.pause_overlay.pause_game()
 var elapsed=game.clock.elapsed
 await create_timer(.1,true).timeout
 assert(game.clock.elapsed==elapsed)
 game.pause_overlay.resume_game()
 game.restart()
 assert(game.weather.strength==0 and game.rain.instances.multimesh.visible_instance_count==1400)
 assert(game.clock.elapsed==0)
 for n in game.find_children("*","",true,false):
  if n is AudioStreamPlayer or n is AudioStreamPlayer3D:n.stop();n.stream=null
 await create_timer(.2).timeout
 game.free();await create_timer(.3).timeout
 print("NEIGHBORHOOD INTEGRATION PASS: authored awning bounds, weather-clock order, pause, reset, note anchor")
 quit()
