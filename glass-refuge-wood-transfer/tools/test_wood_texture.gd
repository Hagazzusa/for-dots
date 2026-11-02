extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var model := (load("res://assets/refuge.glb") as PackedScene).instantiate()
	root.add_child(model)
	await process_frame
	var oak := model.find_child("Opaque_Oak", true, false) as MeshInstance3D
	assert(oak != null)
	var material := oak.mesh.surface_get_material(0) as StandardMaterial3D
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.get_width() == 1024 and material.albedo_texture.get_height() == 1024)
	assert(not material.emission_enabled)
	print("WOOD_TEXTURE_IMPORT_PASS: 1024 albedo texture; no baked emission material")
	model.queue_free()
	await process_frame
	quit()
