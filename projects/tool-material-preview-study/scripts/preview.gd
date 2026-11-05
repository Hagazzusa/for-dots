@tool
extends Node3D
## Isolated experiment. Never edits the original material or imported mesh resource.
@export var preview_material: StandardMaterial3D:
 set(value):
  preview_material = value
  _connect_source()
  _schedule_refresh()
var refresh_count := 0
var _source: StandardMaterial3D
var _queued := false
var _epoch := 0
func _enter_tree() -> void:
 _connect_source()
 _schedule_refresh()
func _connect_source() -> void:
 if _source != null and _source.changed.is_connected(_schedule_refresh):
  _source.changed.disconnect(_schedule_refresh)
 _source = preview_material
 if _source != null:
  _source.changed.connect(_schedule_refresh)
func _schedule_refresh() -> void:
 if not is_inside_tree() or _queued:return
 _queued=true
 _refresh.call_deferred(_epoch)
func _refresh(epoch: int) -> void:
 if epoch != _epoch:return
 _queued=false
 if not is_inside_tree():return
 var imported=get_node_or_null("Imported")
 if imported==null:return
 refresh_count+=1
 for child in imported.find_children("*","MeshInstance3D",true,false):
  child.material_override=preview_material.duplicate() if preview_material!=null else null
func _exit_tree() -> void:
 _epoch+=1
 if _source != null and _source.changed.is_connected(_schedule_refresh):
  _source.changed.disconnect(_schedule_refresh)
 _source=null
 _queued=false
