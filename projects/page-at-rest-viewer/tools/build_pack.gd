extends SceneTree
## External build/audit helper. Never include this script or QA fixtures in the PCK.
var files := {}
var visiting := {}
var failures := 0
const FORBIDDEN := ["qa/", "work/", "tests/", "tools/", "art/", "debug/", "docs/", "export_templates/", "feature_profiles/", "script_templates/", "text_editor_themes/"]
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
 collect("res://scenes/viewer.tscn")
 # Runtime scripts are included; authoring and QA helpers are excluded.
 # Saved scenes follow their actual recursive import/dependency closure.
 walk("res://scripts","runtime")
 add_file("res://project.godot")
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
func run():
 var args=OS.get_cmdline_user_args()
 if args.size()!=1:
  push_error("Pass one output PCK path");quit(2);return
 build(args[0])
 quit(0 if failures==0 else 1)
