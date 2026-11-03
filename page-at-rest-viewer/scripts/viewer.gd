extends Node3D
## Composition owns observation light level, not source geometry or physical emission.
@export var warm_energy := 0.055
@onready var rig=$ViewRig
@onready var warm_light:OmniLight3D=$Lighting/Warm
@onready var status:Label=$UI/Panel/Margin/Rows/Status
const LEVELS := [1.0,0.45,0.0]
var light_index := 0
func _ready()->void:
 get_window().min_size=Vector2i(640,480)
 for mesh in $PageStudy.find_children("*","MeshInstance3D",true,false):
  for i in range(8):
   rig.framing_points.append(rig.to_local(mesh.to_global(mesh.get_aabb().get_endpoint(i))))
 rig.reset_view()
 update_light()
func _unhandled_key_input(event:InputEvent)->void:
 if not event is InputEventKey or not event.pressed or event.echo:return
 var key:Key=event.physical_keycode if event.physical_keycode!=0 else event.keycode
 if key==KEY_L:cycle_light()
 elif key==KEY_R:reset_all()
 else:return
 get_viewport().set_input_as_handled()
func cycle_light()->void:
 light_index=(light_index+1)%LEVELS.size()
 update_light()
func update_light()->void:
 warm_light.light_energy=warm_energy*LEVELS[light_index]
 warm_light.visible=light_index!=2
 status.text="따뜻한 빛 %d%% · 약한 환경광·보조광 유지" % int(LEVELS[light_index]*100)
func reset_all()->void:
 rig.reset_view();light_index=0;update_light()
