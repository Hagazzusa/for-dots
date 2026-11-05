extends Node3D
## Owns only bounded camera observation; no model motion or captured mouse.
@export var target := Vector3(0, 0.055, 0)
@export var initial_yaw := 0.10
@export var initial_pitch := 0.85
@export var initial_distance := 1.45
@export var yaw_limit := 1.15
@export var pitch_min := 0.55
@export var pitch_max := 1.25
@export var distance_min := 1.0
@export var distance_max := 2.6
@export var orbit_speed := 0.65
@export var zoom_speed := 0.55
@export var hero_bounds := AABB(Vector3(-0.285,0,-0.302),Vector3(0.587,0.24,0.643))
var framing_points := PackedVector3Array()
var last_viewport_size := Vector2.ZERO
var yaw: float
var pitch: float
var distance: float
@onready var camera: Camera3D = $Camera3D
func _ready() -> void:
 reset_view()
func key_down(code:Key)->bool:
 return Input.is_physical_key_pressed(code) or Input.is_key_pressed(code)
func _process(delta:float)->void:
 if get_viewport().get_visible_rect().size!=last_viewport_size:update_camera()
 if not get_window().has_focus():return
 var horizontal:=float(key_down(KEY_RIGHT))-float(key_down(KEY_LEFT))
 var vertical:=float(key_down(KEY_UP))-float(key_down(KEY_DOWN))
 var zoom:=float(key_down(KEY_MINUS) or key_down(KEY_KP_SUBTRACT))-float(key_down(KEY_EQUAL) or key_down(KEY_PLUS) or key_down(KEY_KP_ADD))
 if horizontal!=0 or vertical!=0 or zoom!=0:
  move_view(horizontal,vertical,zoom,delta)
func move_view(horizontal:float,vertical:float,zoom:float,delta:float)->void:
 if not is_finite(delta) or delta<0:return
 yaw=clampf(yaw+horizontal*orbit_speed*delta,-yaw_limit,yaw_limit)
 pitch=clampf(pitch+vertical*orbit_speed*delta,pitch_min,pitch_max)
 distance=clampf(distance+zoom*zoom_speed*delta,distance_min,distance_max)
 update_camera()
func reset_view()->void:
 yaw=initial_yaw;pitch=initial_pitch;distance=initial_distance
 update_camera()
func minimum_framing_distance()->float:
 var back:=Vector3(sin(yaw)*cos(pitch),sin(pitch),cos(yaw)*cos(pitch))
 var forward:Vector3=-back
 var right:=forward.cross(Vector3.UP).normalized()
 var up:=right.cross(forward).normalized()
 var size:=get_viewport().get_visible_rect().size
 var aspect:=maxf(size.x/maxf(size.y,1),0.1)
 var top_margin:=maxf(0.20,132.0/maxf(size.y,480.0))
 var bottom_margin:=maxf(0.10,60.0/maxf(size.y,480.0))
 var half_tangent:=tan(deg_to_rad(camera.fov)*0.5)
 var required:=distance_min
 var points:=framing_points.duplicate()
 if points.is_empty():
  for i in range(8):points.append(hero_bounds.get_endpoint(i))
 for point in points:
  var p:Vector3=point-target
  var depth:=p.dot(forward)
  var vertical:=p.dot(up)
  # Reserve help/disclosure pixels even in the smallest supported window.
  required=maxf(required,absf(p.dot(right))/(half_tangent*aspect*0.86)-depth)
  required=maxf(required,absf(vertical)/(half_tangent*(1.0-2.0*top_margin if vertical>=0 else 1.0-2.0*bottom_margin))-depth)
 return required
func update_camera()->void:
 last_viewport_size=get_viewport().get_visible_rect().size
 distance=maxf(distance,minimum_framing_distance())
 camera.position=target+Vector3(sin(yaw)*cos(pitch),sin(pitch),cos(yaw)*cos(pitch))*distance
 camera.look_at(target,Vector3.UP)
