extends Node3D
## Stable authorable world layout. No construction at runtime.
@export var shelter_half_width := 3.6
@export var shelter_half_depth := 1.4
@onready var anchors:Node3D=$BusStop/Anchors
func anchor(id:String)->Vector3:
	return anchors.get_node(id).global_position
func is_sheltered(point:Vector3)->bool:
	return absf(point.x)<shelter_half_width and absf(point.z)<shelter_half_depth
