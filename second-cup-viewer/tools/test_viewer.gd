extends SceneTree
var checks:=0
var failures:Array[String]=[]
func _initialize()->void:call_deferred("run")
func expect(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func dispatch(code:Key,pressed:bool,echo:=false)->void:
 var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=0;e.pressed=pressed;e.echo=echo
 Input.parse_input_event(e)
func run()->void:
 var scene=load("res://scenes/viewer.tscn")
 var v=scene.instantiate();root.add_child(v)
 await process_frame
 var rig=v.rig
 var start:Vector3=rig.camera.position
 expect(rig.framing_points.size()==144,"18 hero mesh bounds exclude tabletop and fallback")
 expect(v.light_on and v.key_light.visible,"default light")
 dispatch(KEY_L,true);await process_frame;dispatch(KEY_L,false);await process_frame
 expect(not v.light_on and not v.key_light.visible,"real logical L dispatch")
 dispatch(KEY_L,true,true);await process_frame;dispatch(KEY_L,false)
 expect(not v.light_on,"echo ignored")
 dispatch(KEY_R,true);await process_frame;dispatch(KEY_R,false)
 expect(v.light_on,"real logical R dispatch")
 dispatch(KEY_RIGHT,true);await process_frame
 expect(rig.key_down(KEY_RIGHT),"logical arrow held state")
 dispatch(KEY_RIGHT,false);await process_frame
 expect(not rig.key_down(KEY_RIGHT),"arrow released state")
 for direction in [-1.0,1.0]:
  rig.move_view(direction,direction,direction,1000.0)
  expect(absf(rig.yaw)<=rig.yaw_limit,"yaw clamp")
  expect(rig.pitch>=rig.pitch_min and rig.pitch<=rig.pitch_max,"pitch clamp")
  expect(rig.distance>=rig.distance_min and rig.distance<=rig.distance_max,"distance clamp")
  expect(rig.camera.position.y>0.5,"camera remains above table")
 for y in [-rig.yaw_limit,0.0,rig.yaw_limit]:
  for p in [rig.pitch_min,rig.initial_pitch,rig.pitch_max]:
   rig.yaw=y;rig.pitch=p;rig.distance=rig.distance_min;rig.update_camera()
   for point in rig.framing_points:
    var pixel:Vector2=rig.camera.unproject_position(rig.to_global(point))
    var size:Vector2=root.get_visible_rect().size
    expect(pixel.x>=size.x*0.069 and pixel.x<=size.x*0.931 and pixel.y>=size.y*0.199 and pixel.y<=size.y*0.901,"hero bounds inside visible margins")
 var before:Vector3=rig.camera.position
 rig.move_view(1,1,1,-2)
 expect(rig.camera.position==before,"negative delta ignored")
 rig.move_view(1,1,1,NAN)
 expect(rig.camera.position==before,"NaN delta ignored")
 for i in range(30):v.toggle_light()
 v.reset_all()
 expect(v.light_on and rig.camera.position.distance_to(start)<0.00001,"reset after repeated toggles")
 expect(v.get_node("Lighting/Fill").visible,"fill remains on")
 expect(v.get_node("Environment").environment.ambient_light_energy>0,"ambient remains positive")
 var second=scene.instantiate();root.add_child(second);await process_frame
 v.toggle_light();rig.move_view(1,1,1,0.2)
 expect(second.light_on,"light instance isolation")
 expect(second.rig.camera.position.distance_to(start)<0.00001,"camera instance isolation")
 var meshes=v.get_node("TeaStudy").find_children("*","MeshInstance3D",true,false)
 expect(meshes.size()>0,"actual GLB meshes loaded")
 var tea_count:=0
 var triangle_count:=0
 for node in meshes:
  for i in range(node.mesh.get_surface_count()):
   triangle_count+=node.mesh.surface_get_array_index_len(i)/3
   var mat=node.get_active_material(i)
   expect(mat!=null,"active surface material")
   if mat!=null and "Amber" in mat.resource_name:
    tea_count+=1
    expect(mat.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED,"tea opaque approximation")
 expect(triangle_count==62072,"full base geometry triangle count")
 expect(tea_count==1,"one tea liquid material surface")
 second.queue_free();v.queue_free();await process_frame
 var third=scene.instantiate();root.add_child(third);await process_frame
 expect(third.light_on and third.rig.camera.position.distance_to(start)<0.00001,"free and fresh instance")
 third.queue_free();await process_frame
 var result={"checks":checks,"failures":failures,"scope":"Headless logic and imported assets; no native visual or physical keyboard claim."}
 print("VIEWER_RESULT ",JSON.stringify(result))
 var report_path:=OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size()>0 else "res://qa/headless_tests.json"
 var file=FileAccess.open(report_path,FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  "));file.close()
 quit(0 if failures.is_empty() else 1)
