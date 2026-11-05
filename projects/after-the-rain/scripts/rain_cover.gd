extends Node3D
## Authorable dry volume under the actual awning; no geometry/light/collision.
## Caller injects the same world AABB into World and Rain.
@export var size := Vector3(3.65,2.605,1.0)

func get_world_bounds() -> AABB:
	return global_transform * AABB(-size*.5,size)
