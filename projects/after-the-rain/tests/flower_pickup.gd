extends SceneTree
var checks:=0
var failures:=0
func check(ok:bool,label:String):
 checks+=1
 if not ok:failures+=1;push_error(label)
func _initialize():call_deferred("run")
func run():
 var s=load("res://scenes/flower_life.tscn")
 var a=s.instantiate();var b=s.instantiate();root.add_child(a);root.add_child(b)
 await process_frame
 var near_point=Vector3(0,0,2)
 var vase:Transform3D=a.get_node("PreparedBouquet/WaterVase").transform
 var wrap:Transform3D=a.get_node("PreparedBouquet/Wrapping").transform
 a.advance(100,near_point,true)
 check(a.can_wave() and not a.pickup.active,"reading preserves first greeting before pickup")
 check(a.request_wave(),"first greeting available")
 a.advance(100,near_point,true)
 a.advance(100,near_point,true)
 check(a.state=="done" and not a.pickup.active,"relevant reader defers pickup start after greeting")
 a.advance(0,near_point,false)
 check(a.pickup.active and not a.pickup.completed,"closing reader permits optional pickup")
 check(not a.request_wave(),"pickup does not add greeting prompt")
 a.advance(3.2,near_point)
 check(a.pickup.customer.visible and a.get_node("PreparedBouquet/Wrapping").position!=wrap.origin,"actual authored customer and bouquet move")
 check(b.state=="idle" and not b.pickup.active and b.get_node("PreparedBouquet/Wrapping").transform==wrap,"two instances independent")
 var t:float=a.pickup.elapsed
 a.advance(NAN,near_point);a.advance(-4,near_point)
 check(a.pickup.elapsed==t,"invalid negative deltas do not corrupt pickup")
 a.advance(100000,near_point)
 check(a.pickup.completed and not a.pickup.active and not a.get_node("PreparedBouquet/Wrapping").visible,"large step completes once with bouquet removed")
 check(a.get_node("PreparedBouquet/WaterVase").transform==vase and a.get_node("PreparedBouquet/WaterVase").visible,"empty vase remains fixed")
 for i in range(20):
  a.advance(0,Vector3(5,0,0));a.advance(100,near_point)
  check(a.pickup.completed and not a.pickup.active,"revisits never duplicate collection")
 a.reset_visit();a.advance(a.dwell_seconds,near_point)
 check(a.state=="window" and a.can_wave(),"later greeting remains without wrapping nonexistent bouquet")
 a.reset()
 check(not a.pickup.completed and not a.pickup.active and a.get_node("PreparedBouquet/Wrapping").visible and a.get_node("PreparedBouquet/Wrapping").transform==wrap,"new night restores bouquet and event")
 a.advance(100,near_point);a.advance(0,near_point);a.advance(3,near_point);a.reset()
 check(a.get_node("PreparedBouquet/Wrapping").transform==wrap and not a.pickup.customer.visible,"reset mid transfer restores exact pose")
 # Sample every 1/60 s of the complete authored event. Bounds are scene-space,
 # not a claim of continuous-time visibility or physical paper simulation.
 a.reset();a.advance(100,near_point);a.advance(0,near_point)
 var bounded:=true
 var fades_match:=true
 var owner_contact:=true
 var customer_contact:=true
 for frame in range(481):
  a.advance(1.0/60.0,near_point)
  var grip:Vector3=a.bouquet_wrap.to_global(Vector3(.02,.11,.02))
  if a.pickup.active and a.pickup.elapsed<=a.pickup.approach_seconds+a.pickup.receive_seconds:
   owner_contact=owner_contact and a.work_hand.global_position.distance_to(grip)<.00001
  if a.pickup.active and a.pickup.elapsed>=a.pickup.approach_seconds+a.pickup.receive_seconds:
   customer_contact=customer_contact and a.pickup.get_node("Customer/Hand").global_position.distance_to(grip)<.045
  for mesh in a.pickup.customer.find_children("*","MeshInstance3D",true,false):
   for corner in range(8):
    var point:Vector3=a.to_local(mesh.to_global(mesh.get_aabb().get_endpoint(corner)))
    bounded=bounded and point.x<=0.7 and point.x>=-1.66
  if a.pickup.active and a.pickup.elapsed>=a.pickup.duration()-.65:
   fades_match=fades_match and is_equal_approx(a.pickup._materials[0].albedo_color.a,a.pickup._bouquet_materials[0].albedo_color.a)
 check(owner_contact,"owner hand follows wrapping throughout sampled transfer")
 check(customer_contact,"customer hand holds wrapping before owner release and through exit")
 check(a.work_hand.transform==a._hand_rest and a.work_sleeve.transform==a._sleeve_rest,"completion restores hand and sleeve exact authored transforms")
 check(bounded,"customer sampled bounds stay inside authored front window width")
 check(fades_match,"customer and carried bouquet share departure visibility")
 check(a._materials[0].albedo_color.a==0 and not a.pickup.customer.visible,"completed departure leaves no floating customer or owner")
 a.free();b.free();await process_frame
 print("FLOWER PICKUP: %d checks / %d failures"%[checks,failures]);quit(1 if failures else 0)
