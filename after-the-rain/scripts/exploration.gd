extends Node3D
## Small optional walk. Held-item and reading-panel dependencies are injected by session.
var umbrella:Node3D
var panel:CanvasLayer
var borrowed := false
@onready var basket = $UmbrellaReturn/Interaction
@onready var flower = $Neighborhood/FlowerWindow/Interaction
var flower_text = preload("res://config/story_flower.tres")
func initialize(held_item:Node3D, reading_panel:CanvasLayer):
 umbrella=held_item
 panel=reading_panel
func aimed(camera:Camera3D,viewer_position:Vector3,point:Vector3)->bool:
 return viewer_position.distance_to(point)<2.0 and (-camera.global_basis.z).dot((point-camera.global_position).normalized())>.88
func hint(camera:Camera3D,viewer_position:Vector3)->String:
 if aimed(camera,viewer_position,basket.global_position):
  return "[E] 우산 제자리에 두기" if borrowed else "[E] 함께 쓰는 우산 빌리기"
 if aimed(camera,viewer_position,flower.global_position):return "[E] 닫힌 꽃집의 작은 쪽지 읽기"
 return ""
func try_interact(camera:Camera3D,viewer_position:Vector3)->bool:
 if aimed(camera,viewer_position,basket.global_position):
  if borrowed:umbrella.return_umbrella()
  else:umbrella.borrow()
  borrowed=umbrella.held
  return true
 if aimed(camera,viewer_position,flower.global_position):
  panel.open_story(flower_text)
  return true
 return false
func reset():
 borrowed=false
 if umbrella:umbrella.reset()
