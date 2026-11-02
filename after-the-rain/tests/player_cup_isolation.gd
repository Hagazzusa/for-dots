extends SceneTree
var intent_count := 0
func _initialize():
	call_deferred("run")
func run():
	var cup_scene := load("res://scenes/cocoa_cup.tscn") as PackedScene
	var a = cup_scene.instantiate()
	var b = cup_scene.instantiate()
	root.add_child(a)
	root.add_child(b)
	assert(a.get_child_count() == 6 and a.has_node("InnerWall") and a.has_node("Bottom"))
	assert(a.liquid_material != b.liquid_material, "Material isolation")
	a.set_fill(0,true)
	assert(a.current_fill == 0 and b.current_fill == 1)
	a.set_fill(1,true)
	for up in [Vector3.UP,Vector3(.6,.8,0),Vector3(1,.01,1),Vector3.DOWN]:
		for i in range(20):
			a.impulse(Vector2(.2,-.2))
			a.update_liquid(1.0/60,up)
		assert(a.max_surface_height <= .076 and a.min_surface_height >= -.08)
	assert(a.liquid.mesh != b.liquid.mesh, "Mesh isolation")
	var player_scene := load("res://scenes/player.tscn") as PackedScene
	var player = player_scene.instantiate()
	var second = player_scene.instantiate()
	root.add_child(player)
	root.add_child(second)
	player.set_physics_process(false)
	second.set_physics_process(false)
	player.reset(Vector3(-4.6,1.65,2.4))
	assert(is_equal_approx(player.camera.fov,67))
	player.sit(Vector3(-1,1.25,-.12))
	assert(player.seated and not second.seated)
	player.stand(Vector3(-1,1.65,1.5))
	assert(not player.seated)
	player.interaction_requested.connect(func(): intent_count += 1)
	var key := InputEventKey.new()
	key.keycode = KEY_E
	key.pressed = true
	player._unhandled_input(key)
	assert(intent_count == 1)
	player.held_drink.set_fill(1,true)
	player.held_drink.present(3,true,0,false,Vector3(1,0,0),0,false,.016,1)
	assert(player.held_drink.visible and not second.held_drink.visible)
	player.held_drink.reset_visuals()
	assert(not player.held_drink.visible)
	var packed := PackedScene.new()
	assert(packed.pack(player) == OK)
	assert(ResourceSaver.save(packed,"user://v4-player-roundtrip.tscn") == OK)
	var reopened = load("user://v4-player-roundtrip.tscn").instantiate()
	root.add_child(reopened)
	reopened.set_physics_process(false)
	assert(reopened.has_node("CollisionShape3D") and reopened.has_node("Camera3D/HeldDrink/Cup/Liquid"))
	for node in [a,b,player,second,reopened]: node.queue_free()
	await process_frame
	print("PLAYER/CUP PASS: saved 6-part hollow vessel, standalone scenes, two-instance mesh/material/state isolation, bounds, intents once, save/reopen")
	quit()
