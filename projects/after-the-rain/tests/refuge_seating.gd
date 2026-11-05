extends SceneTree
var failures:=0
func check(value:bool,label:String):
 print("SEAT ","PASS " if value else "FAIL ",label)
 if not value:failures+=1
func _initialize():call_deferred("run")
func release_session(game:Node):
 # Wait for actual mixer release instead of assuming a fixed delay is enough.
 var pending:Array[WeakRef]=game._prepare_app_shutdown()
 game.queue_free()
 await process_frame
 var deadline:=Time.get_ticks_usec()+2000000
 while Time.get_ticks_usec()<deadline:
  var alive:=false
  for reference in pending:
   if reference.get_ref()!=null:alive=true
  if not alive:
   check(true,"session audio playback released before exit")
   return
  await process_frame
 check(false,"session audio playback released before exit")
func run():
 var g=load("res://main.tscn").instantiate()
 root.add_child(g)
 g.testing=true
 g.set_process(false)
 g.player.input_enabled=false
 g.player.set_physics_process(false)
 await physics_frame
 var n=g.neighborhood
 var sit:Vector3=n.seat_position()
 var stand:Vector3=n.stand_position()
 var bus_stand:Vector3=g.world.anchor("Stand")
 var marker:Transform3D=n.get_node("GlassRefuge/RestSeat/Stand").transform
 check(sit.distance_to(g.world.anchor("Seat"))>5,"two physically different seats")
 check(g.world.is_sheltered(sit) and g.world.is_sheltered(stand),"seat and landing inside dry floor bounds")
 g.player.position=stand
 g.player.camera.look_at(n.get_node("GlassRefuge/RestSeat/Interaction").global_position)
 check(n.can_sit(g.player.camera,g.player.position),"front interior bench target")
 g.story.panel.open_story(n.refuge_text)
 g.interact()
 check(not g.player.seated,"reader advance/close takes priority before new sit")
 g.story.panel.close_story()
 g.interact()
 check(g.player.seated and g.player.position.is_equal_approx(sit),"E sits at authored refuge marker")
 check(g.seated_exit_position.is_equal_approx(stand),"session owns copied refuge exit")
 var saved_rotation:Vector3=g.player.rotation
 g.photo_view()
 check(g.player.seated and g.player.position.is_equal_approx(sit),"overview preserves seat and body")
 g.leave_photo_view()
 check(g.player.seated and g.player.rotation.is_equal_approx(saved_rotation),"overview returns without changing seat")
 g.umbrella.borrow()
 g.umbrella.toggle_open()
 g.drink.request_action(true,false)
 g.drink.advance(3)
 g.drink_action()
 check(g.drink.has_cup and g.umbrella.held and g.drink.sips==2 and g.drink.sip_time>0,"seated sip consumes one serving and preserves held items")
 var elapsed:float=g.clock.elapsed
 g.wait_quietly()
 check(g.bus.phase=="approaching" and g.clock.elapsed>elapsed,"far seated T advances only remaining wait")
 check(g.player.seated and g.player.position.is_equal_approx(sit),"quiet wait never moves player to bus")
 g.bus.advance(100)
 check(g.player.seated and g.player.position.is_equal_approx(sit) and not g.boarded,"missed bus never forces exit/boarding")
 # Both seats use the same truthful reader-first E priority.
 for pair in [[sit,stand],[g.world.anchor("Seat"),bus_stand]]:
  g.sit_at(pair[0],pair[1])
  g.story.panel.open_story(n.car_text)
  g.interact()
  check(g.player.seated and g.player.position.is_equal_approx(pair[0]) and g.story.panel._page==1,"seated E advances page without moving")
  check(not "Stand up" in g.hint_text(),"reader prompt does not falsely advertise standing")
  g.interact()
  check(g.player.seated and not g.story.panel.is_open,"last-page E closes reader without standing")
  g.interact()
  check(not g.player.seated and g.player.position.is_equal_approx(pair[1]),"next E stands at this seat's exit")
  g.sit_at(pair[0],pair[1])
  g.story.panel.open_story(n.car_text)
  var q:=InputEventKey.new()
  q.keycode=KEY_Q
  q.pressed=true
  g.story.panel._unhandled_key_input(q)
  check(g.player.seated and not g.story.panel.is_open,"Q closes reader without standing")
  g.interact()
  check(not g.player.seated and g.player.position.is_equal_approx(pair[1]),"Q then E stands locally")
 # A loan offer may be opened seated; departed passenger cancels it safely.
 g.sit_at(g.world.anchor("Seat"),bus_stand)
 g.story.objects.get_node("Passenger").reset()
 check(g.exchange.request_offer(),"seated loan choice opens")
 g.interact()
 check(g.player.seated and g.exchange.offering,"E does not bypass awaiting loan choice")
 g.story.objects.get_node("Passenger").leave_with_player()
 g.exchange.present(0,"departing")
 check(g.player.seated and not g.story.panel.is_open and not g.exchange.offering,"departing passenger closes loan without moving seated player")
 g.sit_at(sit,stand)
 g.interact()
 # Real capsule after standing must settle on the floor, not inside the bench.
 for i in range(12):
  g.player.velocity=Vector3(0,-1,0)
  g.player.move_and_slide()
  await physics_frame
 check(g.player.is_on_floor() and g.player.position.y>1.59 and g.player.position.y<1.63,"stand landing settles on actual floor")
 check(n.get_node("GlassRefuge/RestSeat/Stand").transform==marker,"saved landing marker remains immutable")
 g.sit_at(g.world.anchor("Seat"),bus_stand)
 g.interact()
 check(g.player.position.is_equal_approx(bus_stand),"original bus bench uses original stand point")
 g.sit_at(sit,stand)
 g.restart()
 check(not g.player.seated and g.seated_exit_position.is_equal_approx(bus_stand),"restart clears active refuge seat identity")
 g.player.position=Vector3(7,1.6,-8.6)
 g.player.camera.look_at(n.get_node("GlassRefuge/RestSeat/Interaction").global_position)
 check(not n.can_sit(g.player.camera,g.player.position),"cannot sit through rear glazing")
 g.player.position=stand
 g.player.camera.look_at(stand+Vector3(0,0,2))
 check(not n.can_sit(g.player.camera,g.player.position),"must face actual bench")
 check(g.seated_exit_position!=stand,"no retained marker reference after reset")
 await release_session(g)
 var fresh=load("res://main.tscn").instantiate()
 root.add_child(fresh)
 fresh.set_process(false)
 fresh.player.input_enabled=false
 check(not fresh.player.seated and fresh.seated_exit_position.is_equal_approx(fresh.world.anchor("Stand")),"new instance has original fresh seat state")
 await release_session(fresh)
 print("REFUGE SEAT FAILURES=",failures)
 quit(failures)
