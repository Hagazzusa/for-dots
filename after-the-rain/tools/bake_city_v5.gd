extends SceneTree
func _initialize():
 call_deferred("build")
func own(n:Node,owner_node:Node):
 n.owner=owner_node
 for c in n.get_children(): own(c,owner_node)
func block(parent:Node3D,name_:String,pos:Vector3,size:Vector3,mat:Material)->MeshInstance3D:
 var n=MeshInstance3D.new()
 n.name=name_
 var m=BoxMesh.new()
 m.size=size
 n.mesh=m
 n.material_override=mat
 parent.add_child(n)
 n.position=pos
 n.owner=parent
 return n
func build():
 var city=load("res://scripts/city_layout.gd").new()
 city.name="CityLayout"
 root.add_child(city)
 assert(city.build(city)==OK,str(city.last_errors))
 var packed=PackedScene.new()
 assert(packed.pack(city)==OK)
 assert(ResourceSaver.save(packed,"res://scenes/city_layout.tscn")==OK)
 city.free()
 var world=load("res://scenes/world.tscn").instantiate()
 root.add_child(world)
 var old=world.get_node("CityBackdrop")
 for c in old.get_children():
  if c.position.z < -5 or c.position.z>18:
   c.free()
 old.name="StreetLighting"
 var baked=load("res://scenes/city_layout.tscn").instantiate()
 world.add_child(baked)
 baked.owner=world
 var road=world.get_node("RoadAndPavement")
 var asphalt=load("res://assets/city/materials/wet_asphalt.tres")
 var concrete=load("res://assets/city/materials/damp_concrete.tres")
 for c in road.get_children():
  if c is MeshInstance3D and c.mesh is BoxMesh:
   if c.mesh.size.x==70: c.material_override=asphalt
   if c.mesh.size.x==18 and c.mesh.size.z==5: c.material_override=concrete
 var sidewalk=Node3D.new()
 sidewalk.name="OppositeSidewalk"
 world.add_child(sidewalk)
 sidewalk.owner=world
 block(sidewalk,"Pavement",Vector3(0,.01,18.6),Vector3(70,.18,3.7),concrete)
 block(sidewalk,"Curb",Vector3(0,.09,16.75),Vector3(70,.14,.18),concrete)
 own(sidewalk,world)
 var env=world.get_node("WorldEnvironment0").environment.duplicate()
 env.fog_density=.014
 world.get_node("WorldEnvironment0").environment=env
 packed=PackedScene.new()
 assert(packed.pack(world)==OK)
 assert(ResourceSaver.save(packed,"res://scenes/world.tscn")==OK)
 world.free()
 print("V5 city baked into authored scene hierarchy")
 quit()
