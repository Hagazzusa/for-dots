extends SceneTree
func _initialize():call_deferred("run")
func dispatch_arrow(key: Key, pressed: bool):
 # Accumulated synthetic input must be flushed before polling its state.
 # Use a fresh event for every edge; physical zero matches native remote arrows.
 var event=InputEventKey.new()
 event.keycode=key;event.physical_keycode=0;event.pressed=pressed
 Input.parse_input_event(event)
 Input.flush_buffered_events()
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
 # Remote arrows may have logical keycode only (physical_keycode=0).
 a.reset(Vector3.ZERO)
 # Initial deferred startup precedes the first accumulated-input flush.
 await process_frame
 await process_frame
 dispatch_arrow(KEY_LEFT,true)
 await process_frame
 assert(Input.is_key_pressed(KEY_LEFT))
 assert(not Input.is_physical_key_pressed(KEY_LEFT))
 before=a.rotation.y
 a._physics_process(.05)
 assert(a.rotation.y>before)
 var held=a.rotation.y
 a._physics_process(.05)
 assert(a.rotation.y>held)
 paused=true
 dispatch_arrow(KEY_LEFT,false);await process_frame
 assert(not Input.is_key_pressed(KEY_LEFT))
 paused=false
 before=a.rotation.y;a._physics_process(.05)
 assert(is_equal_approx(a.rotation.y,before))
 dispatch_arrow(KEY_UP,true);await process_frame
 assert(Input.is_key_pressed(KEY_UP))
 assert(not Input.is_physical_key_pressed(KEY_UP))
 var pitch=a.camera.rotation.x;a._physics_process(.05)
 assert(a.camera.rotation.x>pitch)
 dispatch_arrow(KEY_UP,false);await process_frame
 assert(not Input.is_key_pressed(KEY_UP))
 pitch=a.camera.rotation.x;a._physics_process(.05)
 assert(is_equal_approx(a.camera.rotation.x,pitch))
 a.reset(Vector3(1,2,3))
 assert(not a.seated and a.motion_enabled and a.camera.rotation==Vector3.ZERO)
 a.free();b.free()
 print("KEYBOARD PASS: isolated, seated, pitch bounds, hitch clamp, disabled states, mouse anti-warp, reset")
 quit()
