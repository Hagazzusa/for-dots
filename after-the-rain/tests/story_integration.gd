extends SceneTree
func _initialize():call_deferred("run")
func run():
 var game=load("res://main.tscn").instantiate()
 root.add_child(game)
 await process_frame
 game.testing=true
 game.player.input_enabled=false
 var story=game.story
 for id in ["Memo","Route","Passenger","Radio"]:
  var point:Vector3=story.objects.get_node(id+"/Interaction").global_position
  game.player.position=point+Vector3(0,0,1.4)
  game.player.rotation=Vector3.ZERO
  game.player.camera.look_at(point)
  assert(story.target(game.player.camera,game.player.global_position)==id, "Target "+id)
  assert(story.try_interact(game.player.camera,game.player.global_position))
  if id!="Radio":
   assert(story.panel.is_open)
   story.panel.close_story()
  else: assert(story.radio.is_on)
 story.panel.open_story(story.stories["Memo"])
 game.bus.phase="stopped"
 game.player.position=game.world.anchor("Boarding")
 game.interact()
 assert(game.boarded and not story.panel.is_open and not story.radio.is_on)
 game.restart()
 assert(not game.boarded and not story.panel.is_open and not story.radio.is_on)
 assert(not game.player.seated)
 var packed=PackedScene.new()
 assert(packed.pack(story)==OK)
 assert(ResourceSaver.save(packed,"user://story_roundtrip.tscn")==OK)
 var restored=load("user://story_roundtrip.tscn").instantiate()
 root.add_child(restored)
 assert(restored.objects.has_node("Passenger/Interaction"))
 assert(not restored.panel.is_open and not restored.radio.is_on)
 restored.free()
 game.ambience.stop_all()
 for audio in game.ambience.get_children():
  if audio is AudioStreamPlayer:audio.stream=null
 game.free()
 await create_timer(.3).timeout
 print("STORY INTEGRATION PASS: targeting, repeat/close, board with content open, radio reset, restart")
 quit()
