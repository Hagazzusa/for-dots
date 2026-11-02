extends SceneTree
## External build/audit helper. Never include this script or QA fixtures in the PCK.
var files := {}
var visiting := {}
var failures := 0
const FORBIDDEN := ["tests/", "tools/", "art/", "debug/", "docs/", "export_templates/", "feature_profiles/", "script_templates/", "text_editor_themes/"]
func _initialize(): call_deferred("run")
func fail(message:String):
 failures+=1
 push_error(message)
func allowed(path:String)->bool:
 if not path.begins_with("res://"):return false
 var relative=path.trim_prefix("res://")
 for prefix in FORBIDDEN:
  if relative.begins_with(prefix):return false
 return true
func add_file(path:String):
 if not allowed(path):
  fail("Forbidden runtime dependency: "+path)
  return
 if not FileAccess.file_exists(path):
  fail("Missing runtime file: "+path)
  return
 files[path]=true
func collect(path:String):
 if visiting.has(path):return
 visiting[path]=true
 if not allowed(path):
  fail("Forbidden resource dependency: "+path)
  return
 add_file(path)
 # Imported assets require both their remap and generated native resource files.
 var remap=path+".import"
 if FileAccess.file_exists(remap):
  add_file(remap)
  var cfg=ConfigFile.new()
  if cfg.load(remap)!=OK:
   fail("Unreadable import remap: "+remap)
  else:
   if cfg.has_section("remap"):
    for key in cfg.get_section_keys("remap"):
     if key=="path" or key.begins_with("path."):
      var target=cfg.get_value("remap",key)
      if target is String:collect(target)
   if cfg.has_section_key("deps","dest_files"):
    for target in cfg.get_value("deps","dest_files"):collect(str(target))
 if ResourceLoader.exists(path):
  for dependency in ResourceLoader.get_dependencies(path):
   var parts=String(dependency).split("::")
   var target=parts[parts.size()-1]
   if target.begins_with("res://"):collect(target)
   elif String(dependency).begins_with("uid://"):
    var id=ResourceUID.text_to_id(parts[0])
    if ResourceUID.has_id(id):collect(ResourceUID.get_id_path(id))
    else:fail("Unresolved dependency UID: "+String(dependency))
func walk(directory:String,mode:String):
 var dir=DirAccess.open(directory)
 if dir==null:
  fail("Missing directory: "+directory)
  return
 for name in dir.get_files():
  var path=directory.path_join(name)
  if mode=="all":add_file(path)
  elif mode=="runtime" and path.get_extension() in ["gd","tres","tscn","json","gdshader"]:collect(path)
  elif mode=="licenses" and (name.to_lower().contains("license") or directory.to_lower().contains("licenses")):add_file(path)
 for name in dir.get_directories():walk(directory.path_join(name),mode)
func build(destination:String):
 collect("res://main.tscn")
 # Dynamic config/story loads and runtime scripts are intentionally included.
 # Saved scenes follow their actual recursive import/dependency closure.
 walk("res://scripts","runtime")
 walk("res://config","runtime")
 add_file("res://project.godot")
 if FileAccess.file_exists("res://default_bus_layout.tres"):collect("res://default_bus_layout.tres")
 if DirAccess.dir_exists_absolute("res://assets"):walk("res://assets","licenses")
 if failures:return
 var pack=PCKPacker.new()
 if pack.pck_start(destination)!=OK:
  fail("Cannot create PCK: "+destination);return
 var paths=files.keys();paths.sort()
 for path in paths:
  if pack.add_file(path,path)!=OK:fail("PCK add failed: "+path)
 if pack.flush()!=OK:fail("PCK flush failed")
 var manifest=FileAccess.open(destination+".manifest.json",FileAccess.WRITE)
 if manifest:manifest.store_string(JSON.stringify(paths,"  "))
 else:fail("Cannot write manifest")
 print("PACK BUILD: ",paths.size()," files; ",failures," failures")
func list_pack(directory:String,result:Array):
 var dir=DirAccess.open(directory)
 if dir==null:return
 for name in dir.get_files():result.append(directory.path_join(name))
 for name in dir.get_directories():list_pack(directory.path_join(name),result)
func audit(manifest_path:String):
 var expected=JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
 if not expected is Array:
  fail("Invalid external manifest");return
 var actual:Array=[]
 list_pack("res://",actual)
 for path in actual:
  if not allowed(path):fail("Excluded source fixture packed: "+str(path))
 for path in expected:
  if not FileAccess.file_exists(path):fail("Manifest file absent from isolated pack: "+str(path))
 if ResourceLoader.exists("res://tests/regression.gd"):fail("Test runner leaked into production pack")
 var scene=load("res://main.tscn")
 if not scene is PackedScene:
  fail("Packed main scene failed to load");return
 var game=scene.instantiate()
 root.add_child(game)
 await process_frame
 if game.get("testing")!=false:fail("Production --test enabled fixture mode without runner")
 if game.get_node("Player").get("input_enabled")!=true:fail("Production input disabled")
 for node in [game]+game.find_children("*","",true,false):
  for property in ["text","title"]:
   var value=node.get(property)
   if value is String and (value.contains("TESTONLY") or value.contains("TEST ONLY") or value.contains("TEST FIXTURE")):fail("Test watermark visible in production: "+str(node.get_path()))
 game.set_process(false)
 game.get_node("Player").set_physics_process(false)
 # Let queued audio startup settle, then drain stop before freeing the scene.
 await create_timer(.15).timeout
 for node in game.find_children("*","",true,false):
  if node is AudioStreamPlayer or node is AudioStreamPlayer3D or node is AudioStreamPlayer2D:
   node.stop();node.stream=null
 await create_timer(.15).timeout
 game.queue_free()
 await process_frame
 await create_timer(.15).timeout
 print("PACK AUDIT: ",actual.size()," files, production input enabled, no fixtures; ",failures," failures")
func run():
 var args=OS.get_cmdline_user_args()
 if args.size()>=2 and args[0]=="--build-pck":build(args[1])
 elif args.size()>=2 and args[0]=="--audit-pck":await audit(args[1])
 else:fail("Usage: -- --build-pck DEST | -- --audit-pck MANIFEST [--test]")
 quit(1 if failures else 0)
