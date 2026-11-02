extends SceneTree
func _initialize():call_deferred("run")
func run():
 var scene=load("res://scenes/player.tscn")
 var a=scene.instantiate()
 var b=scene.instantiate()
 root.add_child(a);root.add_child(b)
 a.set_physics_process(false);b.set_physics_process(false)
 var start=a.rotation.y
 a.apply_keyboard_look(Vector2(1,0),.05)
 assert(is_equal_approx(a.rotation.y,start-.05))
 assert(is_equal_approx(b.rotation.y,start))
 a.sit(Vector3.ZERO)
 a.apply_keyboard_look(Vector2(-1,1),.1)
 assert(a.rotation.y>PI and a.camera.rotation.x>-.04)
 for i in range(100):a.apply_keyboard_look(Vector2(0,1),.1)
 assert(is_equal_approx(a.camera.rotation.x,1.15))
 for i in range(100):a.apply_keyboard_look(Vector2(0,-1),.1)
 assert(is_equal_approx(a.camera.rotation.x,-1.15))
 var before=a.rotation.y
 a.apply_keyboard_look(Vector2(1,0),10)
 assert(is_equal_approx(a.rotation.y,before-.1))
 before=a.rotation.y
 a.motion_enabled=false
 a.apply_keyboard_look(Vector2(1,1),.1)
 assert(is_equal_approx(a.rotation.y,before))
 a.motion_enabled=true;a.input_enabled=false
 a.apply_keyboard_look(Vector2(1,1),.1)
 assert(is_equal_approx(a.rotation.y,before))
 a.input_enabled=true
 Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
 var mouse=InputEventMouseMotion.new();mouse.relative=Vector2(200,200)
 a._unhandled_input(mouse)
 assert(is_equal_approx(a.rotation.y,before))
 a.reset(Vector3(1,2,3))
 assert(not a.seated and a.motion_enabled and a.camera.rotation==Vector3.ZERO)
 a.free();b.free()
 print("KEYBOARD PASS: isolated, seated, pitch bounds, hitch clamp, disabled states, mouse anti-warp, reset")
 quit()
