extends Node3D
## One optional pickup per night. The parent injects the authored bouquet pieces.
@export var approach_seconds := 2.0
@export var receive_seconds := 2.2
@export var hold_seconds := 0.8
@export var depart_seconds := 3.0
@onready var customer: Node3D = $Customer
@onready var arrival: Marker3D = $Arrival
@onready var waiting: Marker3D = $Waiting
@onready var exit_point: Marker3D = $Exit
@onready var held_offset: Marker3D = $HeldOffset
var active := false
var completed := false
var elapsed := 0.0
var _pieces: Array[Node3D] = []
var _rests: Array[Transform3D] = []
var _materials: Array[StandardMaterial3D] = []
var _colors: Array[Color] = []
var _bouquet_materials: Array[StandardMaterial3D] = []
var _bouquet_colors: Array[Color] = []

func _ready() -> void:
 for mesh in customer.find_children("*","MeshInstance3D",true,false):
  var mat: StandardMaterial3D = mesh.material_override.duplicate()
  mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
  mesh.material_override = mat
  _materials.append(mat); _colors.append(mat.albedo_color)
 _present()

func initialize(pieces: Array[Node3D]) -> void:
 _pieces = pieces.duplicate()
 _rests.clear()
 for piece in _pieces:
  _rests.append(piece.transform)
  var meshes: Array = [piece] if piece is MeshInstance3D else piece.find_children("*","MeshInstance3D",true,false)
  for mesh in meshes:
   var mat: StandardMaterial3D = mesh.material_override.duplicate()
   mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
   mesh.material_override = mat
   _bouquet_materials.append(mat);_bouquet_colors.append(mat.albedo_color)
 reset_night()

func duration() -> float:
 return maxf(approach_seconds,.01)+maxf(receive_seconds,.01)+maxf(hold_seconds,.01)+maxf(depart_seconds,.01)

func begin() -> bool:
 if active or completed or _pieces.is_empty(): return false
 active = true
 elapsed = 0.0
 _present()
 return true

func advance(delta: float) -> void:
 if not active or not is_finite(delta): return
 elapsed = minf(elapsed+maxf(delta,0.0),duration())
 if elapsed >= duration():
  active = false
  completed = true
 _present()

func reset_night() -> void:
 active = false
 completed = false
 elapsed = 0.0
 _present()

func _present() -> void:
 var a := maxf(approach_seconds,.01)
 var r := maxf(receive_seconds,.01)
 var h := maxf(hold_seconds,.01)
 var d := maxf(depart_seconds,.01)
 var arrive := smoothstep(0.0,a,elapsed)
 var receive := smoothstep(a,a+r,elapsed)
 var depart := smoothstep(a+r+h,a+r+h+d,elapsed)
 customer.position = arrival.position.lerp(waiting.position,arrive).lerp(exit_point.position,depart)
 customer.visible = active
 var opacity := smoothstep(0.0,.5,elapsed)*(1.0-smoothstep(duration()-.65,duration(),elapsed)) if active else 0.0
 for i in range(_materials.size()):
  var color := _colors[i]; color.a *= opacity; _materials[i].albedo_color=color
 var bouquet_opacity := 0.0 if completed else (1.0-smoothstep(duration()-.65,duration(),elapsed))
 for i in range(_bouquet_materials.size()):
  var color := _bouquet_colors[i];color.a*=bouquet_opacity;_bouquet_materials[i].albedo_color=color
 var carry := held_offset.position*receive+(exit_point.position-waiting.position)*depart
 for i in range(_pieces.size()):
  if not is_instance_valid(_pieces[i]):continue
  _pieces[i].transform=_rests[i]
  _pieces[i].position+=carry
  _pieces[i].visible=not completed
