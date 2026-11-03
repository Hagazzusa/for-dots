extends SceneTree
var checks:=0
var failures:=0
func check(ok:bool,label:String):
 checks+=1
 if not ok:failures+=1;push_error(label)
func _initialize():call_deferred("run")
func run():
 var g=load("res://main.tscn").instantiate()
 root.add_child(g);current_scene=g
 await process_frame
 g.set_process(false);g.player.input_enabled=false;g.player.set_physics_process(false)
 var e=g.exploration
 var a=e.flower_life
 var p=a.pickup
 var panel=g.story.panel
 g.player.position=a.to_global(Vector3(0,1,2))
 panel.open_story(e.flower_text)
 var clock_before:float=g.clock.elapsed
 var bus_before:float=g.bus.countdown_seconds()
 var cat_before:float=e.cat.phase
 for i in range(25):g._process(1.0)
 check(a.can_wave() and not p.active,"actual reader preserves first greeting and delays pickup")
 check(g.clock.elapsed>clock_before+24 and g.bus.countdown_seconds()<bus_before-24,"clock and bus continue while actual flower reader is open")
 check(e.cat.phase>cat_before,"cat continues independently while reading")
 panel.close_story();check(a.request_wave(),"original greeting accepted")
 g._process(5.0);g._process(0.0)
 check(p.active and not p.completed,"session starts pickup after first visit")
 # Aim at the actual note marker; no mocked target selection.
 g.player.position=e.flower.global_position+Vector3(0,0,1.5)
 g.player.camera.look_at(e.flower.global_position)
 g.player.input_enabled=true
 var key=InputEventKey.new();key.keycode=KEY_E;key.pressed=true
 Input.parse_input_event(key);await process_frame
 key=InputEventKey.new();key.keycode=KEY_E;key.pressed=false
 Input.parse_input_event(key);await process_frame
 g.player.input_enabled=false
 check(panel.is_open,"real E event dispatch opens pickup note through session")
 check(panel.current_story==e.pickup_flower_text,"active pickup selects truthful arrival observation")
 var saved_pages: Array = panel.current_story.pages.duplicate()
 var before:float=p.elapsed
 g.set_process(true)
 await process_frame;await process_frame
 check(p.elapsed>before,"actual nonpaused processing advances pickup")
 var phase:float=p.elapsed
 var clock_phase:float=g.clock.elapsed
 paused=true
 await create_timer(.1,true).timeout
 check(p.elapsed==phase and g.clock.elapsed==clock_phase,"tree pause stops both pickup and clock")
 paused=false
 await process_frame;await process_frame
 check(p.elapsed>phase,"actual resume advances pickup")
 g.set_process(false)
 g._process(20)
 check(p.completed and panel.is_open and panel.current_story==e.pickup_flower_text and panel.current_story.pages==saved_pages,"completion never replaces an open reading snapshot")
 panel.close_story()
 check(e.try_interact(g.player.camera,g.player.position) and panel.current_story==e.collected_flower_text,"later note interaction selects empty-vase observation")
 panel.close_story()
 a.reset_visit();a.advance(100,Vector3(0,0,2))
 check(p.completed and not p.active,"visit reset cannot replay nightly pickup")
 g.restart();g.set_process(false);g.player.input_enabled=false;g.player.set_physics_process(false)
 check(not p.active and not p.completed and not panel.is_open,"actual new night resets completion and reader")
 g.player.position=a.to_global(Vector3(0,1,2));g._process(100);g._process(0);g._process(3)
 check(p.active,"second night can independently start pickup")
 panel.open_story(e.pickup_flower_text)
 var board_phase:float=p.elapsed
 g.bus.phase="stopped";g.board_bus();g._process(2)
 check(g.boarded and not panel.is_open and p.elapsed==board_phase,"boarding closes reader and stops pickup progression")
 g.restart();g.set_process(false)
 check(not p.active and not p.completed and not p.customer.visible,"restart after boarded pickup restores new-night scene")
 # Authored ownership survives pack/reinstantiate, not just runtime generation.
 var authored=load("res://scenes/flower_life.tscn").instantiate()
 root.add_child(authored);await process_frame
 var packed=PackedScene.new()
 check(packed.pack(authored)==OK,"authored flower scene packs")
 var roundtrip="user://flower_pickup_roundtrip.tscn"
 check(ResourceSaver.save(packed,roundtrip)==OK,"authored packed scene saves to scratch")
 var reopened=ResourceLoader.load(roundtrip,"",ResourceLoader.CACHE_MODE_IGNORE).instantiate();root.add_child(reopened);await process_frame
 check(reopened.get_node("FlowerPickup/Customer").get_child_count()==5 and reopened.get_node("PreparedBouquet").get_child_count()==4,"saved customer and all bouquet parts reopen")
 check(not reopened.pickup.completed and reopened.pickup._materials[0]!=authored.pickup._materials[0],"fresh saved instances isolate state and materials")
 reopened.free();authored.free()
 DirAccess.remove_absolute(ProjectSettings.globalize_path(roundtrip))
 g.app_shutdown.initialize(g,g._prepare_app_shutdown,func():pass)
 g.app_shutdown.request_shutdown()
 var deadline:int=Time.get_ticks_usec()+3000000
 while not g.app_shutdown.finished and Time.get_ticks_usec()<deadline:await process_frame
 check(g.app_shutdown.finished,"bounded normal shutdown completes")
 g.free();await process_frame
 print("FLOWER PICKUP INTEGRATION: %d checks / %d failures"%[checks,failures])
 quit(1 if failures else 0)
