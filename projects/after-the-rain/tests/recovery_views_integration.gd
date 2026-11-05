extends SceneTree
func _initialize():call_deferred("run")
func key(code:Key):
 var event=InputEventKey.new();event.keycode=code;event.pressed=true
 Input.parse_input_event(event);Input.flush_buffered_events()
 await process_frame
 event=InputEventKey.new();event.keycode=code;event.pressed=false
 Input.parse_input_event(event);Input.flush_buffered_events()
 await process_frame
func run():
 var g=load("res://main.tscn").instantiate();root.add_child(g)
 g.set_process(false);g.player.set_physics_process(false)
 await process_frame;await process_frame
 g.restart();g.player.sit(g.world.anchor("Seat"))
 g.story.panel.open_story(g.story.stories["Memo"])
 var pose=g.player.transform;var camera_pose=g.player.camera.transform
 var page=g.story.panel._page
 await key(KEY_P)
 assert(g.photo_mode and g.overview.camera.current and not g.player.motion_enabled)
 assert(g.player.transform==pose and g.player.seated and g.story.panel.is_open)
 assert(g.story.panel.suspended and not g.story.panel.visible)
 await key(KEY_Q);await key(KEY_1)
 assert(g.story.panel.is_open and g.story.panel._page==page)
 var mouse=InputEventMouseMotion.new();mouse.relative=Vector2(20,10)
 g.player._unhandled_input(mouse)
 assert(g.player.transform==pose and g.player.camera.transform==camera_pose)
 await key(KEY_E)
 assert(not g.photo_mode and g.player.seated and g.player.motion_enabled)
 assert(g.player.camera.current and g.story.panel.is_open and g.story.panel._page==page)
 assert(g.story.panel.visible and not g.story.panel.suspended)
 g.umbrella.borrow();g.photo_view();g._process(0)
 assert(not "[U]" in g.hud.hint.text)
 g.restart()
 assert(not g.photo_mode and not g.story.panel.suspended and g.player.camera.current)
 g.bus.phase="stopped";g.board_bus();g.onboard.advance(9)
 assert(g.ride_finished and not g.onboard.linger)
 g.interact();assert(g.onboard.linger and g.ride_finished)
 g._process(0);assert(not g.hud.ending.visible)
 g.interact();g._process(0);assert(not g.onboard.linger and g.hud.ending.visible)
 g.restart();assert(not g.onboard.linger and not g.ride_finished)
 g.rain.set_view_position(Vector3(15,3,15))
 assert(g.rain.proximity_scale(Vector3(15,3,15))==0)
 assert(g.rain.proximity_scale(Vector3(17,3,15))==1)
 assert(g.rain.proximity_scale(Vector3(16,3,15))>0 and g.rain.proximity_scale(Vector3(16,3,15))<1)
 var before=g.rain.drops.duplicate();g.rain.set_view_position(Vector3.ZERO)
 assert(g.rain.drops==before)
 for n in g.find_children("*","",true,false):
  if n is AudioStreamPlayer or n is AudioStreamPlayer3D:n.stop();n.stream=null
 await create_timer(.2).timeout
 g.free();await create_timer(.3).timeout
 print("VIEWS INTEGRATION PASS: real P/E, seated pose/reader preservation, no hidden choice, linger ending/reset, near-view rain")
 quit()
