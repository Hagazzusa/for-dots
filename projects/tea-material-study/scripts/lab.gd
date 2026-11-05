extends Node3D
## Only the copied tea mesh material is overridden. Fixed, bounded QA matrix.
const SOURCE_GLB_SHA := "e5b3a05b8db4421d1cca41c7f8f30d266ca718533d2602c40a1bad2e34416a7b"
const TEA_SHADER = preload("res://shaders/empirical_tea.gdshader")
const CUP_CENTER := Vector3(-0.17,0.034,0.165)
const VIEWS := ["high","oblique","low"]
const OFFSETS := [Vector3(0.035,0.36,0.28),Vector3(-0.24,0.20,0.28),Vector3(0.32,0.034,0.24)]
@onready var camera:Camera3D = $Camera
@onready var key:DirectionalLight3D = $Key
@onready var status:Label = $UI/Status
var tea:MeshInstance3D
var candidate_material:ShaderMaterial
var candidate := false
var view_index := 0
var key_on := true
var captured:Array[Dictionary] = []
var geometry_before := ""
func _ready() -> void:
    get_window().min_size=Vector2i(720,640)
    for node in $Tableau.find_children("*","MeshInstance3D",true,false):
        if node.name=="NearCup_Tea": tea=node
    assert(tea!=null,"Tea mesh was not imported")
    assert(FileAccess.get_sha256("res://assets/second_cup_tableau.glb")==SOURCE_GLB_SHA,"Source GLB differs")
    candidate_material=ShaderMaterial.new()
    candidate_material.shader=TEA_SHADER
    geometry_before=geometry_fingerprint()
    update_case()
    if "--capture-matrix" in OS.get_cmdline_user_args():call_deferred("capture_matrix")
func update_case() -> void:
    tea.material_override=candidate_material if candidate else null
    camera.position=CUP_CENTER+OFFSETS[view_index]
    camera.look_at(CUP_CENTER,Vector3.UP)
    key.visible=key_on
    status.text="%s | %s view | key %s" % ["EMPIRICAL CANDIDATE" if candidate else "OPAQUE BASELINE",VIEWS[view_index],"on" if key_on else "off"]
func _unhandled_key_input(event:InputEvent) -> void:
    if not event is InputEventKey or not event.pressed or event.echo:return
    match event.physical_keycode:
        KEY_B:candidate=not candidate
        KEY_V:view_index=(view_index+1)%VIEWS.size()
        KEY_L:key_on=not key_on
        KEY_ESCAPE:get_tree().quit();return
        _:return
    update_case()
func capture_matrix() -> void:
    assert(DisplayServer.get_name()!="headless","Actual display/OpenGL required")
    await get_tree().create_timer(0.5).timeout
    get_window().size=Vector2i(720,640)
    await get_tree().create_timer(0.5).timeout
    for use_candidate in [false,true]:
        candidate=use_candidate
        for i in range(VIEWS.size()):
            view_index=i
            for use_key in [true,false]:
                key_on=use_key
                update_case()
                await get_tree().create_timer(0.22).timeout
                await RenderingServer.frame_post_draw
                var image:Image=get_viewport().get_texture().get_image()
                var mode:String="candidate" if candidate else "opaque"
                var light:String="on" if key_on else "off"
                var name:String="%s_%s_%s.png" % [mode,VIEWS[view_index],light]
                assert(image.save_png("res://qa/"+name)==OK,"Native save failed")
                captured.append({"file":"qa/"+name,"material":mode,"view":VIEWS[view_index],"key_light":light,
                  "camera_position":[camera.position.x,camera.position.y,camera.position.z],
                  "look_at":[CUP_CENTER.x,CUP_CENTER.y,CUP_CENTER.z],"resolution":[image.get_width(),image.get_height()]})
    candidate=false;view_index=0;key_on=true;update_case();tea.visible=false
    await get_tree().create_timer(0.22).timeout
    await RenderingServer.frame_post_draw
    var reference:Image=get_viewport().get_texture().get_image()
    assert(reference.save_png("res://qa/reference_high_on_no_liquid.png")==OK)
    tea.visible=true
    var geometry_after:String=geometry_fingerprint()
    assert(geometry_before==geometry_after,"Runtime geometry changed")
    var report:Dictionary={"engine":Engine.get_version_info().string,
      "display_server":DisplayServer.get_name(),"video_adapter":RenderingServer.get_video_adapter_name(),
      "rendering_method":RenderingServer.get_current_rendering_method(),
      "glb_sha256":FileAccess.get_sha256("res://assets/second_cup_tableau.glb"),
      "candidate_shader_sha256":FileAccess.get_sha256("res://shaders/empirical_tea.gdshader"),
      "captures":captured,"capture_count":captured.size(),
      "diagnostic_reference":"qa/reference_high_on_no_liquid.png",
      "geometry_fingerprint_before":geometry_before,"geometry_fingerprint_after":geometry_after,
      "view_only_material_override":true,"source_geometry_modified":false}
    var file:=FileAccess.open("res://qa/native_matrix.json",FileAccess.WRITE)
    assert(file!=null);file.store_string(JSON.stringify(report,"  ")+"\n");file.close()
    print("TEA_LAB_NATIVE_MATRIX_COMPLETE ",captured.size())
    get_tree().quit()

func geometry_fingerprint() -> String:
    var context:=HashingContext.new()
    context.start(HashingContext.HASH_SHA256)
    for node in $Tableau.find_children("*","MeshInstance3D",true,false):
        context.update(String(node.name).to_utf8_buffer())
        for surface in range(node.mesh.get_surface_count()):
            var arrays:Array=node.mesh.surface_get_arrays(surface)
            context.update(var_to_bytes([arrays[Mesh.ARRAY_VERTEX],arrays[Mesh.ARRAY_NORMAL],arrays[Mesh.ARRAY_INDEX]]))
    return context.finish().hex_encode()
