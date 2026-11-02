extends Node3D
## Small optional walk. Held-item and reading-panel dependencies are injected by session.
signal note_requested(text:String, duration:float)
var umbrella:Node3D
var panel:CanvasLayer
var borrowed := false
var shared_available:Callable
func basket_available()->bool:
 return not shared_available.is_valid() or shared_available.call()
@onready var basket = $UmbrellaReturn/Interaction
@onready var flower_life = $Neighborhood/FlowerWindow/FlowerLife
@onready var cat = $Neighborhood/FlowerWindow/RainCat
@onready var rain_cover = $Neighborhood/FlowerWindow/RainCover
@onready var flower = $Neighborhood/FlowerWindow/Interaction
var flower_text = preload("res://config/story_flower.tres")
func initialize(held_item:Node3D, reading_panel:CanvasLayer):
 umbrella=held_item
 panel=reading_panel
 if not flower_life.caption_requested.is_connected(_on_caption):flower_life.caption_requested.connect(_on_caption)
 if not cat.caption_requested.is_connected(_on_caption):cat.caption_requested.connect(_on_caption)
func _on_caption(text:String):
 note_requested.emit(text,5.0)
func advance(delta:float,viewer_position:Vector3,lull:float):
 flower_life.advance(delta,flower_life.to_local(viewer_position))
 cat.advance(delta,lull)
func life_target(camera:Camera3D,viewer_position:Vector3)->String:
 if cat.can_greet() and aimed(camera,viewer_position,cat.get_node("Interaction").global_position):return "cat"
 if flower_life.can_wave() and aimed(camera,viewer_position,flower_life.get_node("Interaction").global_position):return "flower"
 return ""
func aimed(camera:Camera3D,viewer_position:Vector3,point:Vector3)->bool:
 return viewer_position.distance_to(point)<2.0 and (-camera.global_basis.z).dot((point-camera.global_position).normalized())>.88
func hint(camera:Camera3D,viewer_position:Vector3)->String:
 var target=life_target(camera,viewer_position)
 if target=="cat":return "[E] 고양이에게 조용히 인사하기"
 if target=="flower":return "[E] 꽃집 안쪽에 손 흔들기"
 if aimed(camera,viewer_position,basket.global_position):
  if not basket_available():return "우산은 승객에게 빌려주었다. 바구니는 비어 있다."
  return "[E] 우산 제자리에 두기" if borrowed else "[E] 함께 쓰는 우산 빌리기"
 if aimed(camera,viewer_position,flower.global_position):return "[E] 닫힌 꽃집의 작은 쪽지 읽기"
 return ""
func try_interact(camera:Camera3D,viewer_position:Vector3)->bool:
 var target=life_target(camera,viewer_position)
 if target=="cat":return cat.request_greeting()
 if target=="flower":return flower_life.request_wave()
 if aimed(camera,viewer_position,basket.global_position):
  if not basket_available():return true
  if borrowed:umbrella.return_umbrella()
  else:umbrella.borrow()
  borrowed=umbrella.held
  return true
 if aimed(camera,viewer_position,flower.global_position):
  panel.open_story(flower_text)
  return true
 return false
func reset():
 flower_life.reset()
 cat.reset()
 borrowed=false
 if umbrella:umbrella.reset()
