@tool
extends Resource
## Authoring-only inputs. The generated scene, not this recipe, is used at runtime.
@export_range(1, 24, 1) var buildings_per_row: int = 8
@export_range(1.0, 30.0, .1) var spacing: float = 8.0
@export var layout_seed: int = 7305
@export var rear_row_z: float = -14.0
@export var across_road_z: float = 23.0
@export_range(.1, 30.0, .1) var building_width: float = 7.0
@export_range(.1, 30.0, .1) var building_depth: float = 5.0
@export_range(.1, 100.0, .1) var building_height: float = 12.0
@export_range(0.0, 10.0, .1) var minimum_gap: float = 1.0
@export var clear_street_z: Vector2 = Vector2(-2.0, 18.0)
@export_range(.1, 3.0, .01) var minimum_height_scale: float = .75
@export_range(.1, 3.0, .01) var maximum_height_scale: float = 1.25
@export_range(32, 10000, 1) var node_budget: int = 4096
@export var variants: Array[String] = ["res://scenes/buildings/brick_midrise.tscn", "res://scenes/buildings/plaster_midrise.tscn"]

func validation_errors() -> PackedStringArray:
	var errors := PackedStringArray()
	if buildings_per_row < 1 or buildings_per_row > 24:
		errors.append("Building count must be between 1 and 24 per row.")
	if building_width <= 0 or building_depth <= 0 or building_height <= 0:
		errors.append("Building envelope dimensions must be positive.")
	if minimum_gap < 0 or spacing < building_width + minimum_gap:
		errors.append("Spacing must be at least building_width + minimum_gap.")
	if clear_street_z.x >= clear_street_z.y:
		errors.append("Clear street range must be ordered.")
	if rear_row_z + building_depth * .5 > clear_street_z.x:
		errors.append("Rear row intrudes into the clear street.")
	if across_road_z - building_depth * .5 < clear_street_z.y:
		errors.append("Across-road row intrudes into the clear street.")
	if minimum_height_scale <= 0 or maximum_height_scale < minimum_height_scale:
		errors.append("Height scale range must be positive and ordered.")
	if variants.is_empty():
		errors.append("At least one building variant is required.")
	if node_budget < 1:
		errors.append("Node budget must be positive.")
	return errors
