extends SceneTree
func _initialize():call_deferred("run")
func run():
 var script=load("res://scripts/drink_session.gd")
 for duration in [.65,1.3,2.6]:
  var drink=script.new();root.add_child(drink)
  drink.sip_seconds=duration
  assert(drink.sip_progress()==-1 and drink.cup_heat()==0)
  assert(drink.request_action(true,false));drink.advance(drink.dispense_seconds)
  assert(drink.sips==3 and drink.cup_age==0 and drink.cup_heat()==1)
  assert(drink.request_action(false,false))
  assert(drink.sip_progress()==0 and drink.sips==2)
  assert(not drink.request_action(false,false))
  drink.advance(duration*.5)
  assert(is_equal_approx(drink.sip_progress(),.5))
  drink.advance(duration*.5)
  assert(drink.sip_progress()==-1)
  drink.advance(180)
  assert(is_equal_approx(drink.cup_heat(),.18))
  drink.advance(10000);assert(is_equal_approx(drink.cup_heat(),.18))
  var age=drink.cup_age;drink.advance(-10);drink.advance(NAN)
  assert(drink.cup_age==age)
  for i in range(2):
   assert(drink.request_action(false,false));drink.advance(duration)
  assert(drink.sips==0 and drink.cup_heat()==0)
  assert(drink.dispose_empty() and drink.cup_age==0)
  assert(drink.request_action(true,false));drink.advance(drink.dispense_seconds)
  assert(drink.cup_heat()==1 and drink.cup_age==0)
  drink.reset();assert(drink.sip_progress()==-1 and drink.cup_heat()==0)
  drink.free()
 # The approved default half-sip pose agrees with its old seconds formula.
 var game=load("res://main.tscn").instantiate();root.add_child(game)
 game.set_process(false);game.player.set_physics_process(false);game.player.input_enabled=false
 game.restart();game.drink.request_action(true,false);game.drink.advance(1.2)
 game._process(0)
 assert(game.player.held_drink.visible)
 game.drink.request_action(false,false);game.drink.advance(.65);game._process(0)
 var held=game.player.held_drink
 assert(is_equal_approx(held.global_rotation.x,held.resting_tilt+held.sip_tilt))
 game.photo_view();game._process(0);assert(not held.visible)
 game.leave_photo_view();game._process(0);assert(held.visible)
 game.restart();assert(game.drink.cup_heat()==0 and not held.visible)
 for n in game.find_children("*","",true,false):
  if n is AudioStreamPlayer or n is AudioStreamPlayer3D:n.stop();n.stream=null
 await create_timer(.2).timeout
 game.free();await create_timer(.3).timeout
 print("DRINK TIMING PASS: sole normalized owner, .65/1.3/2.6 variants, cooling bounds/refill, approved midpoint pose, overview/reset")
 quit()
