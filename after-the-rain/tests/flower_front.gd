extends SceneTree
var checks:=0
var failures:=0
func check(ok:bool,label:String):
 checks+=1
 if not ok:failures+=1;push_error(label)
func _initialize():call_deferred("run")
func run():
 var e=load("res://scenes/exploration.tscn").instantiate()
 var panel=load("res://scenes/story_panel.tscn").instantiate()
 var camera=Camera3D.new()
 root.add_child(e);root.add_child(panel);root.add_child(camera)
 e.initialize(null,panel);await process_frame
 var f=e.flower_life
 var z:float=f.front_plane.position.z
 check(is_equal_approx(f.front_plane.global_position.z,-6.0),"saved plane aligns opaque shop front")
 check(f.is_front_side(Vector3(0,0,z)) and f.is_front_side(Vector3(0,0,z+.001)),"front boundary and just ahead accepted")
 check(not f.is_front_side(Vector3(0,0,z-.001)) and not f.is_front_side(Vector3(NAN,0,2)),"behind boundary and nonfinite rejected")
 var side=Vector3(-7.058595,1.599868,-6.700754)
 camera.position=side;camera.look_at(e.flower.global_position)
 check(e.aimed(camera,side,e.flower.global_position),"native-reproduced side still passes original distance and facing")
 check(not e.flower_front(camera,side) and e.hint(camera,side)=="" and not e.try_interact(camera,side) and not panel.is_open,"opaque side cannot hint or read flower note")
 for point in [Vector3(-7.75,1.65,-4.6),Vector3(-6.9,1.65,-5.7),Vector3(-8.5,1.65,-4.7)]:
  camera.position=point;camera.look_at(e.flower.global_position)
  check(e.flower_front(camera,point) and e.try_interact(camera,point) and panel.is_open,"valid front or oblique reading remains "+str(point))
  panel.close_story()
 var front=Vector3(-7.75,1.65,-4.6)
 camera.position=side;camera.look_at(e.flower.global_position)
 check(not e.flower_front(camera,front),"front body cannot interact through a rear camera")
 camera.position=front;camera.look_at(e.flower.global_position)
 check(not e.flower_front(camera,side),"front camera cannot bypass rear body eligibility")
 f.advance(100,f.to_local(side))
 check(f.state=="idle" and not f.pickup.active,"side dwell never starts visit or pickup")
 f.advance(.5,Vector3(0,0,2));f.advance(.1,f.to_local(side))
 check(f.state=="idle","moving behind facade cancels incomplete dwell")
 f.advance(5,Vector3(0,0,2))
 camera.position=side;camera.look_at(f.get_node("Interaction").global_position)
 check(f.can_wave() and e.life_target(camera,side)!="flower","existing window cannot be greeted from side")
 f.advance(100,f.to_local(side),true)
 check(f.state=="done" and not f.pickup.active,"side reader does not hold greeting window")
 f.advance(100,f.to_local(side))
 check(not f.pickup.active,"completed visit does not trigger pickup behind facade")
 f.advance(0,Vector3(0,0,2));f.advance(3,f.to_local(side))
 check(f.pickup.active and is_equal_approx(f.pickup.elapsed,3),"already started pickup continues when viewer leaves front")
 f.advance(100,f.to_local(side));f.advance(0,Vector3(7,0,0))
 check(f.pickup.completed and not f.pickup.active,"visit rearm preserves one-time completion")
 f.reset();check(not f.pickup.completed and f.state=="idle","new night remains sole pickup reset")
 e.cat.advance(3,1)
 var cat_point:Vector3=e.cat.get_node("Interaction").global_position
 camera.position=cat_point+Vector3(0,.3,.8);camera.look_at(cat_point)
 check(e.life_target(camera,camera.position)=="cat","separate cat target remains available")
 e.free();panel.free();camera.free();await process_frame
 print("FLOWER FRONT: %d checks / %d failures"%[checks,failures]);quit(1 if failures else 0)
