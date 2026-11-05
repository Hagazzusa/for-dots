extends SceneTree
func _initialize():
 var w=load("res://scenes/world.tscn").instantiate()
 root.add_child(w)
 for item in [["RoadAndPavement/MeshInstance2",3.0,"wet_asphalt_uv"],["RoadAndPavement/MeshInstance4",2.2,"damp_concrete_uv"],["OppositeSidewalk/Pavement",2.2,"damp_concrete_uv"]]:
  var n=w.get_node(item[0])
  var size=n.mesh.size
  var p=PlaneMesh.new()
  p.size=Vector2(size.x,size.z)
  n.position.y+=size.y*.5
  n.mesh=p
  var m=load("res://assets/city/materials/"+item[2]+".tres").duplicate()
  m.uv1_scale=Vector3(size.x/item[1],size.z/item[1],1)
  n.material_override=m
 var s=PackedScene.new()
 assert(s.pack(w)==OK)
 assert(ResourceSaver.save(s,"res://scenes/world.tscn")==OK)
 w.free()
 quit()
