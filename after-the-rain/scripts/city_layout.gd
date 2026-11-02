@tool
extends Node3D
## Explicit authoring baker. Never generates or consumes RNG on scene ready/play.
const Layout = preload("res://config/city_layout.gd")
@export var layout: Layout = preload("res://config/city_layout.tres")
@export_tool_button("Rebuild preview") var rebuild_action: Callable = rebuild_preview
var last_errors: PackedStringArray = []

func rebuild_preview() -> void:
	if not Engine.is_editor_hint():
		return
	var edited_root := get_tree().edited_scene_root
	if build(edited_root) != OK:
		push_warning("City layout unchanged: " + "; ".join(last_errors))

## scene_owner is the edited/baked scene root, an ancestor of this node or self.
## Existing children outside Generated are never touched. Invalid builds preserve preview.
func build(scene_owner: Node) -> Error:
	last_errors.clear()
	if scene_owner == null or (scene_owner != self and not scene_owner.is_ancestor_of(self)):
		last_errors.append("Scene owner must be this node or an ancestor.")
		return ERR_INVALID_PARAMETER
	if layout == null:
		last_errors.append("Missing city layout Resource.")
		return ERR_INVALID_PARAMETER
	last_errors = layout.validation_errors()
	if not last_errors.is_empty():
		return ERR_INVALID_PARAMETER
	var scenes: Array[PackedScene] = []
	for path in layout.variants:
		if not ResourceLoader.exists(path, "PackedScene"):
			last_errors.append("Missing building variant: " + path)
			return ERR_FILE_NOT_FOUND
		var scene = load(path) as PackedScene
		if scene == null:
			last_errors.append("Variant is not a PackedScene: " + path)
			return ERR_INVALID_DATA
		scenes.append(scene)
	var generated := Node3D.new()
	generated.name = "Generated"
	var rng := RandomNumberGenerator.new()
	rng.seed = layout.layout_seed
	for row in range(2):
		for index in range(layout.buildings_per_row):
			var variant := rng.randi_range(0, scenes.size()-1)
			var building = scenes[variant].instantiate()
			if not building is Node3D:
				building.free()
				generated.free()
				last_errors.append("Building root must be Node3D.")
				return ERR_INVALID_DATA
			generated.add_child(building)
			building.name = ("Rear" if row == 0 else "Across") + "_%02d" % index
			building.position = Vector3((index-(layout.buildings_per_row-1)*.5)*layout.spacing, 0, layout.rear_row_z if row == 0 else layout.across_road_z)
			building.rotation.y = 0.0 if row == 0 else PI
			building.scale = Vector3(1, rng.randf_range(layout.minimum_height_scale, layout.maximum_height_scale), 1)
			building.set_meta("city_variant", layout.variants[variant])
	if count_nodes(generated) > layout.node_budget:
		generated.free()
		last_errors.append("Generated hierarchy exceeds configured node budget.")
		return ERR_OUT_OF_MEMORY
	var old := get_node_or_null("Generated")
	if old != null:
		remove_child(old)
		old.free()
	add_child(generated)
	generated.owner = scene_owner
	for building in generated.get_children():
		building.owner = scene_owner
	# Imported/instanced descendants retain their local scene ownership.
	return OK

func count_nodes(node: Node) -> int:
	var total := 1
	for child in node.get_children():
		total += count_nodes(child)
	return total
