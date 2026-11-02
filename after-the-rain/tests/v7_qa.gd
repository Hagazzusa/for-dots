extends SceneTree
var failures:=0
func check(ok:bool, message:String):
 if ok: print("QA PASS: ",message)
 else:
  failures+=1
  print("QA FAIL: ",message)
func _initialize():call_deferred("run")
func run():
 var g=load("res://main.tscn").instantiate()
 root.add_child(g)
 g.testing=true
 g.set_process(false)
 g.player.input_enabled=false
 g.player.set_physics_process(false)
 await physics_frame
 await physics_frame
 # Reproduce a genuinely ordered narrative interaction, not isolated APIs.
 var p=g.story.objects.get_node("Passenger/Interaction").global_position
 g.player.position=p+Vector3(0,0,1.4)
 g.player.camera.look_at(p)
 check(g.story.try_interact(g.player.camera,g.player.position),"passenger greeting targeted")
 g.story.panel.close_story()
 g.story.advance_passenger(20,"stopped",g.world.anchor("Boarding"))
 check(g.story.objects.get_node("Passenger").state=="boarded","passenger boarded independently")
 var flower=g.exploration.flower.global_position
 g.player.position=flower+Vector3(0,0,1.4)
 g.player.camera.look_at(flower)
 check(g.exploration.try_interact(g.player.camera,g.player.position),"flower note targeted")
 check(g.story.panel.is_open,"flower note initially opens")
 g.story.advance_passenger(.016,"waiting",g.world.anchor("Boarding"))
 check(g.story.panel.is_open,"flower note survives next update after prior passenger conversation")
 g.restart()
 g.story.panel.close_story()
 # Move an actual capsule along plausible left-side walk, retaining collision response.
 g.player.position=Vector3(-4.6,1.65,2.4)
 var route=[Vector3(-8,1.65,2.4),Vector3(-8,1.65,-3.8),Vector3(-9.38,1.65,-4.3)]
 for target in route:
  for i in range(600):
   var d=target-g.player.position
   d.y=0
   if d.length()<.06:break
   g.player.velocity=d.normalized()*2.4+Vector3(0,-1,0)
   if g.player.position.z < 2.5 and g.player.position.z > 1.95 and g.player.velocity.z < 0 and g.player.is_on_floor():
    g.player.position.y=maxf(g.player.position.y,1.64)
   g.player.move_and_slide()
   await physics_frame
  check(Vector2(g.player.position.x-target.x,g.player.position.z-target.z).length()<.1,"physical route waypoint %s reached at %s"%[target,g.player.position])
 g.player.camera.look_at(flower)
 check(g.exploration.aimed(g.player.camera,g.player.position,flower),"flower reachable with actual capsule at floor height")
 g.umbrella.borrow()
 g.umbrella.toggle_open()
 g.drink.request_action(true,false)
 g.drink.advance(5)
 check(g.drink.has_cup and g.umbrella.held and g.umbrella.is_open,"umbrella and cocoa coexist")
 g.bus.phase="stopped"
 g.board_bus()
 check(g.boarded and not g.umbrella.visible and not g.story.panel.is_open,"boarding closes reading and hides umbrella")
 g.restart()
 check(not g.umbrella.held and not g.exploration.borrowed and not g.drink.has_cup and not g.boarded,"restart clears item and boarding state")
 # Multiple natural-size bus cycles: passenger boards once and never ghosts back.
 var stops:=0
 var prior="waiting"
 var moving_seconds=g.bus.schedule.approach_seconds+g.bus.schedule.stop_seconds+g.bus.schedule.departure_seconds
 var three_cycles=g.bus.schedule.wait_seconds+moving_seconds+2*(g.bus.schedule.repeat_wait_seconds+moving_seconds)+1
 for i in range(ceili(three_cycles/.1)):
  g.bus.advance(.1)
  g.story.advance_passenger(.1,g.bus.phase,g.world.anchor("Boarding"))
  if g.bus.phase=="stopped" and prior!="stopped":stops+=1
  prior=g.bus.phase
 check(stops>=3 and g.story.objects.get_node("Passenger").state=="boarded","three bus cycles keep passenger aboard")
 g.restart()
 # Shared basket is usable via E, and return does not remove cocoa.
 var basket=g.exploration.basket.global_position
 g.player.position=basket+Vector3(0,0,1.2)
 g.player.camera.look_at(basket)
 g.interact()
 check(g.umbrella.held and g.exploration.borrowed,"E borrows umbrella")
 g.drink.request_action(true,false)
 g.drink.advance(2)
 g.interact()
 check(not g.umbrella.held and not g.exploration.borrowed and g.drink.has_cup,"E returns umbrella while retaining cocoa")
 g.story.panel.open_story(g.exploration.flower_text)
 g.bus.phase="stopped"
 g.player.position=g.world.anchor("Boarding")
 g.interact()
 check(g.boarded,"E boarding takes precedence over reading")
 g.ambience.stop_all()
 for audio in g.ambience.get_children():
  if audio is AudioStreamPlayer:audio.stream=null
 await create_timer(.5).timeout
 g.queue_free()
 await process_frame
 print("INDEPENDENT QA COMPLETE failures=",failures)
 quit(failures)
