extends SceneTree
var checks:=0
var failures:=0
func check(value:bool,label:String):
 checks+=1
 print("RADIO DIAL ","PASS " if value else "FAIL ",label)
 if not value:failures+=1
func _initialize():call_deferred("run")
func key(code:Key):
 var event:=InputEventKey.new()
 event.keycode=code;event.pressed=true;Input.parse_input_event(event)
 await process_frame
 event=InputEventKey.new();event.keycode=code;event.pressed=false;Input.parse_input_event(event)
 await process_frame
func run():
 var dependencies=ResourceLoader.get_dependencies("res://scenes/stories/small_radio.tscn")
 check(Array(dependencies).any(func(path):return str(path).ends_with("res://assets/materials/radio_dial_lit.tres")),"saved scene explicitly declares the material dependency")
 var scene=load("res://scenes/story_corner.tscn")
 var a=scene.instantiate();var b=scene.instantiate()
 root.add_child(a);root.add_child(b)
 var av=a.objects.get_node("Radio");var bv=b.objects.get_node("Radio")
 check(not a.radio.is_on and not av.powered and av.tuner.material_override==av._off_material,"initial off state matches authored surface")
 check(av._off_material!=bv._off_material and av._on_material!=bv._on_material and av._on_material!=av.lit_material,"two instances own private cached materials")
 var off=av._off_material;var on=av._on_material
 var camera:=Camera3D.new();root.add_child(camera)
 camera.position=av.get_node("Interaction").global_position+Vector3(0,.6,1.0)
 camera.look_at(av.get_node("Interaction").global_position)
 check(a.hint(camera,camera.position)=="[E] 작은 라디오 켜기","off action hint")
 check(a.try_interact(camera,camera.position) and a.radio.is_on and av.powered,"existing interaction toggles matching light")
 check(av.tuner.material_override==on and on.emission_enabled and not bv.powered,"on emits locally and leaves second radio off")
 check(a.hint(camera,camera.position)=="[E] 작은 라디오 끄기" and not a.panel.is_open,"on hint and no reader opened")
 a.radio.set_muted(true)
 check(av.powered and a.radio.is_on,"mute is not power off")
 paused=true;await create_timer(.04,true).timeout
 check(av.powered and av.tuner.material_override==on,"pause preserves on appearance")
 paused=false
 for i in range(20):a.radio.toggle()
 check(av.powered and av._on_material==on and av._off_material==off,"repeated toggles reuse private cached resources")
 on.emission=Color.RED
 check(bv._on_material.emission!=Color.RED and av.lit_material.emission!=Color.RED,"changing a copy cannot mutate source or second scene")
 a.leave()
 check(not a.radio.is_on and not av.powered and av.tuner.material_override==off,"leaving for bus restores off")
 b.radio.toggle();b.reset()
 check(not bv.powered,"new-night reset restores second radio")
 a.radio.toggle();a.radio.begin_shutdown();a.radio.toggle()
 check(not av.powered and not a.radio.is_on,"terminal shutdown clears light and blocks restart")
 b.radio.begin_shutdown()
 # Saved/default material values remain unchanged across state changes.
 check(not off.emission_enabled and off.albedo_color.is_equal_approx(Color(.72,.41,.13,1)),"off appearance preserves original tuner values")
 check(av.find_children("*","Light3D",true,false).is_empty(),"no dynamic light introduced")
 var fallback=load("res://scenes/stories/small_radio.tscn").instantiate()
 fallback.lit_material=null;fallback.set_powered(true);root.add_child(fallback)
 check(fallback.powered,"pre-ready injected power preserved")
 check(fallback.tuner.material_override==fallback._off_material,"null configured material safely falls back")
 fallback.free();camera.free()
 await create_timer(.2).timeout
 a.free();b.free();await process_frame
 var g=load("res://main.tscn").instantiate();root.add_child(g)
 g.set_process(false);g.player.set_physics_process(false)
 var visual=g.story.objects.get_node("Radio")
 g.player.position=Vector3(.95,1.6,1.6);g.player.rotation.y=0
 g.player.camera.look_at(visual.get_node("Interaction").global_position)
 await key(KEY_E)
 check(g.story.radio.is_on and visual.powered,"real session E turns on audio state and dial")
 await key(KEY_M)
 check(visual.powered and g.story.radio.is_on,"actual global M preserves power state")
 g.pause_overlay.pause_game();await key(KEY_E)
 check(not paused and visual.powered,"resume E does not toggle radio")
 await key(KEY_E)
 check(not visual.powered and not g.story.radio.is_on,"next real E turns off")
 await key(KEY_E);await key(KEY_R)
 check(not visual.powered and not g.story.radio.is_on,"real R resets radio and dial")
 g.story.radio.toggle();g.bus.phase="stopped";g.player.position=g.world.anchor("Boarding")
 await key(KEY_E)
 check(g.boarded and not visual.powered and not g.story.radio.is_on,"actual boarding E resets radio and dial")
 g.app_shutdown.initialize(g,g._prepare_app_shutdown,func():pass)
 g.app_shutdown.request_shutdown()
 while not g.app_shutdown.finished:await process_frame
 g.free();await process_frame
 print("RADIO DIAL: %d checks / %d failures"%[checks,failures])
 quit(1 if failures else 0)
