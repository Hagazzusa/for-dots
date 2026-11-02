extends Node3D
## Scene composition and key-light state; asset and camera remain independent.
@onready var rig=$ViewRig
@onready var key_light:DirectionalLight3D=$Lighting/Key
@onready var status:Label=$UI/Panel/Margin/Rows/Status
var light_on:=true
func _ready()->void:
 get_window().min_size=Vector2i(640,480)
 for mesh in $TeaStudy.find_children("*","MeshInstance3D",true,false):
  if mesh.name=="Tabletop":continue
  for i in range(8):
   rig.framing_points.append(rig.to_local(mesh.to_global(mesh.get_aabb().get_endpoint(i))))
 rig.reset_view()
 update_status()
func _unhandled_key_input(event:InputEvent)->void:
 if not event is InputEventKey or not event.pressed or event.echo:return
 var key:Key=event.physical_keycode if event.physical_keycode!=0 else event.keycode
 if key==KEY_L:toggle_light()
 elif key==KEY_R:reset_all()
 else:return
 get_viewport().set_input_as_handled()
func toggle_light()->void:
 light_on=not light_on
 key_light.visible=light_on
 update_status()
func reset_all()->void:
 rig.reset_view();light_on=true;key_light.visible=true;update_status()
func update_status()->void:
 status.text="주광원 %s · 약한 환경광은 유지됩니다" % ("켜짐" if light_on else "꺼짐")
