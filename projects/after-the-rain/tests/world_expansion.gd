extends SceneTree
var failures:=0
func check(value:bool,label:String):
 print("WORLD ","PASS " if value else "FAIL ",label)
 if not value:failures+=1
func _initialize():call_deferred("run")
func walk(g,target:Vector3):
 for i in range(800):
  var d:Vector3=target-g.player.position
  d.y=0
  if d.length()<0.07:break
  g.player.velocity=d.normalized()*2.4+Vector3(0,-1,0)
  if g.player.position.z<2.5 and g.player.position.z>1.95 and g.player.velocity.z<0 and g.player.is_on_floor():g.player.position.y=maxf(g.player.position.y,1.64)
  g.player.move_and_slide()
  await physics_frame
 check(Vector2(g.player.position.x-target.x,g.player.position.z-target.z).length()<0.1,"physical route "+str(target)+" actual "+str(g.player.position))
func run():
 var g=load("res://main.tscn").instantiate()
 root.add_child(g)
 g.testing=true
 g.set_process(false)
 g.player.input_enabled=false
 g.player.set_physics_process(false)
 await physics_frame
 await physics_frame
 var n=g.neighborhood
 check(n.get_node("GlassRefuge").panes.size()==24,"24 private transparent panes")
 var other=load("res://scenes/neighborhood_extension.tscn").instantiate()
 root.add_child(other)
 other.initialize(g.story.panel)
 check(n.heater.stream!=other.heater.stream,"independent per-instance heater stream")
 check(n.get_node("GlassRefuge").panes[0].material_override!=other.get_node("GlassRefuge").panes[0].material_override,"private pane materials")
 n.advance(0.1)
 check(other.elapsed==0,"local animation phase isolation")
 other.queue_free()
 await process_frame
 for resource in [n.car_text,n.refuge_text,g.exploration.flower_text]:
  for text in resource.pages:
   g.story.panel.body_label.text=text
   await process_frame
   check(g.story.panel.body_label.get_minimum_size().y<202,"new Korean page fits reader")

 check(n.get_node("ParkedCar/Driver")!=null and n.get_node("ParkedCar/Passenger")!=null,"exact two authored occupant roots")
 # Actual capsule motion starts at ordinary spawn; no teleport to the new pocket.
 for p in [Vector3(-5,1.6,1.6),Vector3(-5,1.6,-3.6),Vector3(8,1.6,-3.6),Vector3(8,1.6,-5.5),Vector3(7,1.6,-6.2)]:await walk(g,p)
 check(g.world.is_sheltered(g.player.position),"inside refuge dry sound volume")
 check(g.rain.additional_shelters.size()==2,"same new cover delivered to rain")
 for p in [Vector3(8,1.6,-5.5),Vector3(8,1.6,-3.6),Vector3(13,1.6,-3.1)]:await walk(g,p)
 g.player.camera.look_at(n.get_node("CarObservation").global_position)
 check(n.target(g.player.camera,g.player.position)=="Car","outside passenger-side observation targeted")
 g.interact()
 check(g.story.panel.current_story==n.car_text,"E opens optional two-sibling reader")
 g.story.panel.close_story()
 var before:float=n.elapsed
 g.set_process(true)
 await process_frame
 await process_frame
 check(n.elapsed>before,"ordinary processing advances vignette before pause")
 var phase:float=n.elapsed
 paused=true
 await create_timer(0.1,true).timeout
 check(n.elapsed==phase,"tree pause does not advance vignette")
 paused=false
 await process_frame
 await process_frame
 check(n.elapsed>phase,"resume restores ordinary vignette processing")
 g.set_process(false)
 for p in [Vector3(9.5,1.6,-3.6),Vector3(4.5,1.6,-3.6),Vector3(4.5,1.6,1.5),g.world.anchor("Boarding")]:await walk(g,p)
 g.story.panel.open_story(n.car_text)
 g.bus.phase="stopped"
 g.interact()
 check(g.boarded and not g.story.panel.is_open,"board priority closes new story")
 g._process(0.01)
 check(not n.enabled and not n.heater.playing,"board suspends local heater")
 g.restart()
 check(n.enabled and n.elapsed==0 and not g.story.panel.is_open,"restart resets independent vignette")
 g.ambience.stop_all()
 n.heater.stop()
 n.heater.stream=null
 g.queue_free()
 await process_frame
 await create_timer(.2).timeout
 print("WORLD EXPANSION FAILURES=",failures)
 quit(failures)
