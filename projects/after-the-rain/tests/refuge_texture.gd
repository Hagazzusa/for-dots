extends SceneTree
var failures := 0
func check(value:bool, label:String):
 print("WOOD ","PASS " if value else "FAIL ",label)
 if not value:failures+=1
func _initialize():call_deferred("run")
func run():
 var scene=load("res://scenes/neighborhood_extension.tscn").instantiate()
 root.add_child(scene)
 await process_frame
 var meshes=scene.get_node("GlassRefuge/Imported").find_children("*","MeshInstance3D",true,false)
 var surfaces:=0
 var triangles:=0
 var textured:=0
 for mesh in meshes:
  surfaces+=mesh.mesh.get_surface_count()
  for i in range(mesh.mesh.get_surface_count()):
   var arrays=mesh.mesh.surface_get_arrays(i)
   triangles+=arrays[Mesh.ARRAY_INDEX].size()/3
   var mat=mesh.mesh.surface_get_material(i) as StandardMaterial3D
   if mat and mat.albedo_texture:
    textured+=1
    check(str(mesh.name)=="Opaque_Oak","only oak has baked albedo")
    check(mat.albedo_texture.get_width()==512 and mat.albedo_texture.get_height()==512,"embedded512 texture imported")
    check(not mat.emission_enabled,"wood not unlit/emissive")
    check(mesh.material_override==null,"wrapper preserves textured material")
    var active=mesh.get_active_material(i) as StandardMaterial3D
    check(active==mat and active.albedo_texture==mat.albedo_texture,"active surface retains verified oak texture")
 check(meshes.size()==33 and surfaces==35 and triangles==78388,"geometry count contract")
 check(textured==1,"one textured surface")
 check(scene.get_node("GlassRefuge").panes.size()==24,"glass override contract")
 check(scene.get_node("GlassRefuge/PendantLight").visible,"dynamic pendant retained")
 scene.queue_free()
 await process_frame
 quit(1 if failures else 0)
