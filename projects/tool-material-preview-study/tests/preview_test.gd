extends SceneTree
var count := 0
var failures := 0
func check(ok:bool,label:String):
 count+=1
 print("PREVIEW ","PASS " if ok else "FAIL ",label)
 if not ok:failures+=1
func flush():
 await process_frame
 await process_frame
func mats(pair):
 return pair.get_node("Imported").find_children("*","MeshInstance3D",true,false)
func _initialize():call_deferred("run")
func run():
 var packed=load("res://scenes/main.tscn")
 var main=packed.instantiate()
 # Explicit fixture: the saved editor evidence leaves PairA null.
 main.get_node("PairA").preview_material=load("res://assets/blue.tres")
 main.get_node("PairB").preview_material=load("res://assets/blue.tres")
 root.add_child(main)
 await flush()
 var a=main.get_node("PairA");var b=main.get_node("PairB")
 var source=a.preview_material
 var blue=source.albedo_color
 var ap=mats(a);var bp=mats(b)
 check(ap.size()==2 and bp.size()==2,"two panes two instances")
 check(ap[0].material_override!=ap[1].material_override and ap[0].material_override!=bp[0].material_override,"per pane independent copies")
 ap[0].material_override.albedo_color=Color.RED
 check(source.albedo_color==blue and bp[0].material_override.albedo_color==blue,"preview mutation not source/other instance")
 var before=a.refresh_count
 source.albedo_color=Color.GREEN
 await flush()
 print("OBSERVATION direct setter refresh delta=",a.refresh_count-before)
 source.emit_changed()
 await flush()
 check(a.refresh_count==before+1,"one refresh for source change")
 check(ap[0].material_override.albedo_color==Color.GREEN and bp[0].material_override.albedo_color==Color.GREEN,"shared source intentionally updates both")
 source.albedo_color=blue
 source.emit_changed()
 await flush()
 var amber=load("res://assets/amber.tres")
 a.preview_material=amber
 await flush()
 before=a.refresh_count
 var other_before=b.refresh_count
 source.roughness=.6
 source.emit_changed()
 await flush()
 check(a.refresh_count==before and b.refresh_count==other_before+1,"old signal detached with other-instance positive control")
 check(ap[0].material_override.albedo_color==amber.albedo_color and bp[0].material_override.albedo_color==blue,"replacement only changes chosen instance")
 for i in range(5):a.preview_material=amber
 await flush()
 before=a.refresh_count
 amber.roughness=.7
 amber.emit_changed()
 await flush()
 check(a.refresh_count==before+1,"repeated assignment has one connection")
 a.preview_material=null
 await flush()
 check(ap[0].material_override==null and ap[1].material_override==null,"null restores imported material")
 a.preview_material=source
 source.roughness=.45;amber.roughness=.45
 source.emit_changed()
 await flush()
 main.remove_child(a)
 await flush()
 main.add_child(a)
 a.owner=main # Restore original serialization ownership after deliberate detach.
 await flush()
 before=a.refresh_count
 source.emit_changed()
 await flush()
 check(a.refresh_count==before+1,"reattach restores source subscription")
 var saved=PackedScene.new()
 check(saved.pack(main)==OK,"pack authored sandbox")
 var args=OS.get_cmdline_user_args()
 var dest=args[0]
 check(ResourceSaver.save(saved,dest)==OK,"save to external QA copy")
 var text=FileAccess.get_file_as_string(dest)
 check(not text.contains("material_override") and not text.contains('type="StandardMaterial3D"'),"runtime preview copies not serialized in packed root")
 main.queue_free()
 await flush()
 var reopened=load(dest).instantiate();root.add_child(reopened)
 await flush()
 check(mats(reopened.get_node("PairA"))[0].material_override.albedo_color==blue,"saved copy reopen restores preview")
 reopened.queue_free()
 await flush()
 check(source.changed.get_connections().is_empty() and amber.changed.get_connections().is_empty(),"signal connections removed after free")
 print("PREVIEW SUMMARY ",count," checks ",failures," failures")
 quit(1 if failures else 0)
