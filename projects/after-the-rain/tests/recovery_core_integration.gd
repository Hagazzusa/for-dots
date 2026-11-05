extends SceneTree
func _initialize():call_deferred("run")
func run():
 var game=load("res://main.tscn").instantiate()
 root.add_child(game)
 game.player.input_enabled=false
 await process_frame
 assert(not game.bus.visual.visible)
 game.story.panel.open_story(game.story.stories["Memo"])
 var page=game.story.panel._page
 assert(game.pause_overlay.pause_game())
 var before=game.bus.phase_time
 await create_timer(.08,true,false,true).timeout
 assert(game.bus.phase_time==before)
 assert(game.story.panel.is_open and game.story.panel._page==page)
 game.pause_overlay.resume_game()
 assert(not paused and game.story.panel.is_open)
 game.restart()
 assert(not game.story.panel.is_open and not game.pause_overlay.active)
 assert(not game.bus.visual.visible and not game.boarded)
 game.bus.advance(game.bus.effective_wait_seconds()+1);game.bus.advance(9)
 assert(game.bus.phase=="stopped" and game.bus.visual.visible)
 game.board_bus()
 assert(game.boarded and not game.bus.visible and game.bus.paused)
 assert(game.pause_overlay.pause_game())
 var elapsed=game.onboard.elapsed
 await create_timer(.08,true,false,true).timeout
 assert(game.onboard.elapsed==elapsed)
 game.pause_overlay.new_evening()
 assert(not paused and not game.boarded and game.bus.visible and not game.bus.visual.visible)
 game.ambience.stop_all()
 for node in game.find_children("*","",true,false):
  if node is AudioStreamPlayer or node is AudioStreamPlayer3D:
   node.stop();node.stream=null
 await create_timer(.2).timeout
 game.free()
 await create_timer(.3).timeout
 print("CORE INTEGRATION PASS: reader pause, bus clock freeze, boarding pause, restart state")
 quit()
