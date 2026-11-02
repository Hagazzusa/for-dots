extends SceneTree
func _initialize():call_deferred("run")
func run():
 var g=load("res://main.tscn").instantiate();root.add_child(g)
 g.set_process(false);g.player.set_physics_process(false);g.player.input_enabled=false
 g.restart();g.player.position=g.disposal_point.global_position
 g.drink.has_cup=true;g.drink.sips=0
 assert(g.drink.can_dispose_empty())
 g.story.panel.open_story(g.story.stories["Memo"])
 assert(not "bin" in g.hint_text())
 g.interact();assert(g.story.panel._page==1 and g.drink.has_cup)
 g.interact();assert(not g.story.panel.is_open and g.drink.has_cup)
 assert("bin" in g.hint_text())
 g.interact();assert(not g.drink.has_cup)
 g.drink.has_cup=true;g.drink.sips=1;g.drink.request_action(false,false)
 assert(not g.drink.can_dispose_empty() and not "bin" in g.hint_text())
 g.interact();assert(g.drink.has_cup)
 g.drink.advance(g.drink.sip_seconds)
 assert(g.drink.can_dispose_empty() and "bin" in g.hint_text())
 g.drink.request_action(true,false)
 assert(not g.drink.can_dispose_empty() and not "bin" in g.hint_text())
 g.drink.advance(g.drink.dispense_seconds)
 assert(g.drink.sips==3 and not g.drink.can_dispose_empty())
 g.story.panel.open_story(g.story.stories["Memo"])
 g.player.position=g.world.anchor("Boarding")
 g.bus.advance(g.bus.effective_wait_seconds());g.bus.advance(g.bus.schedule.approach_seconds)
 g.interact();assert(g.boarded and not g.story.panel.is_open)
 g.restart();assert(not g.drink.has_cup and not g.story.panel.is_open)
 for n in g.find_children("*","",true,false):
  if n is AudioStreamPlayer or n is AudioStreamPlayer3D:n.stop();n.stream=null
 await create_timer(.2).timeout
 g.free();await create_timer(.3).timeout
 print("READER DISPOSAL PASS: reader before bin, final sip/refill readiness, boarding override, reset")
 quit()
