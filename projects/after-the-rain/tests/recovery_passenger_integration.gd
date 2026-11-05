extends SceneTree
func _initialize():call_deferred("run")
func prepare_bus(g):
 g.bus.advance(g.bus.effective_wait_seconds());g.bus.advance(8)
func advance_bus(g,seconds:float):
 for i in range(int(seconds/.1)):
  g.bus.advance(.1)
  g.story.advance_passenger(.1,g.bus.phase,g.world.anchor("Boarding")+Vector3(0,0,.65))
  g.exchange.present(.1,g.bus.phase)
func run():
 var g=load("res://main.tscn").instantiate();root.add_child(g)
 g.set_process(false);g.player.set_physics_process(false);g.player.input_enabled=false
 g.restart();var person=g.story.objects.get_node("Passenger")
 prepare_bus(g);g.board_bus()
 assert(g.boarded and not g.companion.visible)
 g.restart();prepare_bus(g);advance_bus(g,15)
 assert(person.state=="boarded" and not person.departed)
 g.board_bus();assert(g.companion.visible)
 g.restart();prepare_bus(g);advance_bus(g,29)
 assert(person.state=="boarded" and person.departed and not g.exchange.loaned)
 prepare_bus(g);g.board_bus();assert(not g.companion.visible)
 g.restart()
 var greeting=g.conversation.next_story();g.story.panel.open_story(greeting);g.story.panel.close_story()
 var question=g.conversation.next_story();g.story.panel.open_story(question);g.story.panel.select_choice(0);g.story.panel.close_story()
 var memory=g.conversation.ride_memory();assert(not memory.is_empty())
 prepare_bus(g);g.board_bus();assert(g.ride_note==memory)
 g.restart()
 greeting=g.conversation.next_story();g.story.panel.open_story(greeting);g.story.panel.close_story()
 question=g.conversation.next_story();g.story.panel.open_story(question);g.story.panel.select_choice(1);g.story.panel.close_story()
 g.umbrella.borrow();assert(g.exchange.request_offer());g.story.panel.select_choice(0);g.story.panel.close_story()
 prepare_bus(g);advance_bus(g,15);g.board_bus()
 assert(g.companion.visible and g.ride_note==g.exchange.boarding_caption(true))
 assert(g.ride_note!=g.conversation.ride_memory())
 g.restart();assert(not g.companion.visible and not person.departed and g.conversation.ride_memory().is_empty())
 for n in g.find_children("*","",true,false):
  if n is AudioStreamPlayer or n is AudioStreamPlayer3D:n.stop();n.stream=null
 await create_timer(.2).timeout
 g.free();await create_timer(.3).timeout
 print("PASSENGER INTEGRATION PASS: actual early/same/later bus without loan, reason/loan memory priority, reset")
 quit()
