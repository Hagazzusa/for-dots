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
 expect(rig.framing_points.size()==72,"9 mesh bounds include book and sculpture")
 expect(v.light_index==0 and v.warm_light.visible,"default light")
 dispatch(KEY_L,true);await process_frame;dispatch(KEY_L,false);await process_frame
 expect(v.light_index==1 and v.warm_light.visible,"real logical L dispatch")
 dispatch(KEY_L,true,true);await process_frame;dispatch(KEY_L,false)
 expect(v.light_index==1,"echo ignored")
 dispatch(KEY_R,true);await process_frame;dispatch(KEY_R,false)
 expect(v.light_index==0,"real logical R dispatch")
 dispatch(KEY_RIGHT,true);await process_frame
 expect(rig.key_down(KEY_RIGHT),"logical arrow held state")
 dispatch(KEY_RIGHT,false);await process_frame
 expect(not rig.key_down(KEY_RIGHT),"arrow released state")
 for direction in [-1.0,1.0]:
  rig.move_view(direction,direction,direction,1000.0)
  expect(absf(rig.yaw)<=rig.yaw_limit,"yaw clamp")
  expect(rig.pitch>=rig.pitch_min and rig.pitch<=rig.pitch_max,"pitch clamp")
  expect(rig.distance>=rig.distance_min and rig.distance<=rig.distance_max,"distance clamp")
  expect(rig.camera.position.y>0.0,"camera remains above base")
 for viewport_size in [Vector2i(1100,800),Vector2i(640,480),Vector2i(640,900)]:
  root.size=viewport_size
  await process_frame
  for y in [-rig.yaw_limit,0.0,rig.yaw_limit]:
   for p in [rig.pitch_min,rig.initial_pitch,rig.pitch_max]:
    rig.yaw=y;rig.pitch=p;rig.distance=rig.distance_min;rig.update_camera()
    for point in rig.framing_points:
     var pixel:Vector2=rig.camera.unproject_position(rig.to_global(point))
     var size:Vector2=root.get_visible_rect().size
     expect(pixel.x>=size.x*0.069 and pixel.x<=size.x*0.931 and pixel.y>=size.y*0.199 and pixel.y<=size.y*0.901,"hero bounds inside visible margins")
 root.size=Vector2i(1100,800)
 await process_frame
 var before:Vector3=rig.camera.position
 rig.move_view(1,1,1,-2)
 expect(rig.camera.position==before,"negative delta ignored")
 rig.move_view(1,1,1,NAN)
 expect(rig.camera.position==before,"NaN delta ignored")
 for i in range(30):v.cycle_light()
 v.reset_all()
 expect(v.light_index==0 and rig.camera.position.distance_to(start)<0.00001,"reset after repeated toggles")
 expect(v.get_node("Lighting/Fill").visible,"fill remains on")
 expect(v.get_node("Environment").environment.ambient_light_energy>0,"ambient remains positive")
 var second=scene.instantiate();root.add_child(second);await process_frame
 v.cycle_light();rig.move_view(1,1,1,0.2)
 expect(second.light_index==0,"light instance isolation")
 expect(second.rig.camera.position.distance_to(start)<0.00001,"camera instance isolation")
 var meshes=v.get_node("PageStudy").find_children("*","MeshInstance3D",true,false)
 expect(meshes.size()>0,"actual GLB meshes loaded")
 var paper_count:=0
 var triangle_count:=0
 for node in meshes:
  for i in range(node.mesh.get_surface_count()):
   triangle_count+=node.mesh.surface_get_array_index_len(i)/3
   var mat=node.get_active_material(i)
   expect(mat!=null,"active surface material")
   if mat!=null and mat is ShaderMaterial:
    paper_count+=1
    expect(not "ALPHA" in mat.shader.code and not "EMISSION" in mat.shader.code,"paper opaque non-emissive approximation")
 expect(triangle_count==199840,"full base geometry triangle count")
 expect(paper_count==2,"two paper shader surfaces")
 var paper=v.get_node("PageStudy").find_child("LeftPage",true,false)
 var other=second.get_node("PageStudy").find_child("LeftPage",true,false)
 expect(paper.material_override!=other.material_override,"paper material instance isolation")
 expect(paper.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF,"paper shadow approximation explicit")
 expect(is_equal_approx(paper.material_override.get_shader_parameter("backlight_strength"),0.35),"bounded paper backlight")
 for level in range(3):
  v.light_index=level;v.update_light()
  expect(is_equal_approx(v.warm_light.light_energy,v.warm_energy*v.LEVELS[level]),"three light energies")
  expect(v.warm_light.visible==(level!=2),"zero warm light hidden")
 second.queue_free();v.queue_free();await process_frame
 var third=scene.instantiate();root.add_child(third);await process_frame
 expect(third.light_index==0 and third.rig.camera.position.distance_to(start)<0.00001,"free and fresh instance")
 third.queue_free();await process_frame
 var result={"checks":checks,"failures":failures,"scope":"Headless logic and imported assets; no native visual or physical keyboard claim."}
 print("VIEWER_RESULT ",JSON.stringify(result))
 var report_path:=OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size()>0 else "res://qa/headless_tests.json"
 var file=FileAccess.open(report_path,FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  "));file.close()
 quit(0 if failures.is_empty() else 1)
