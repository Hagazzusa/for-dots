extends Node3D
## Explicit runtime-only paper approximation; never edits the imported mesh/material.
@export var paper_material:Material
var paper_count:=0
func _ready()->void:
 assert(paper_material!=null,"Paper approximation must be authored explicitly")
 for mesh in find_children("*","MeshInstance3D",true,false):
  if mesh.name in ["LeftPage","RightPage"]:
   mesh.material_override=paper_material.duplicate()
   mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
   paper_count+=1
 assert(paper_count==2,"Expected two authored page meshes")
