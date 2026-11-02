extends Node3D
## Optional local content. No references to gameplay siblings; session supplies view/location.
@export var interaction_radius := 2.3
@export var facing_threshold := 0.72 # Passenger: broad, welcoming gaze.
@export var paper_facing_threshold := 0.95
@export var radio_facing_threshold := 0.94
@onready var panel = $StoryPanel
@onready var radio = $RadioAudio
@onready var objects = $Objects
var stories := {}
var active_story := ""
var passenger_story_provider: Callable
var passenger_prompt_provider: Callable
const PROMPTS = {"Memo":"[E] 정류장에 남겨진 메모 읽기", "Route":"[E] 08번 노선도 살펴보기", "Passenger":"[E] 비를 피하는 승객에게 인사하기", "Radio":"[E] 작은 라디오 켜기 / 끄기"}
func _ready():
 panel.closed.connect(func(): active_story="")
 for id in ["Memo", "Route", "Passenger"]:
  stories[id] = load("res://config/story_"+id.to_lower()+".tres")
 radio.global_position = objects.get_node("Radio/Interaction").global_position
func threshold_for(id:String)->float:
 if id=="Radio":return radio_facing_threshold
 if id in ["Memo","Route"]:return paper_facing_threshold
 return facing_threshold
func target(camera:Camera3D, viewer_position:Vector3)->String:
 if camera==null:return ""
 var selected := ""
 var best := 0.0
 for id in PROMPTS:
  if id=="Passenger" and not objects.get_node("Passenger").is_available():continue
  var point:Vector3 = objects.get_node(id+"/Interaction").global_position
  if viewer_position.distance_to(point)>interaction_radius: continue
  var direction:Vector3 = (point-camera.global_position).normalized()
  var facing:float = (-camera.global_basis.z).dot(direction)
  if facing > threshold_for(id) and facing > best:
   selected=id
   best=facing
 return selected
func hint(camera:Camera3D, viewer_position:Vector3)->String:
 if panel.is_open: return "[Q] 이야기 닫기 · 버스가 오면 바로 타도 괜찮아요"
 var id := target(camera,viewer_position)
 if id=="Passenger" and passenger_prompt_provider.is_valid():
  return str(passenger_prompt_provider.call())
 return PROMPTS.get(id,"")
func try_interact(camera:Camera3D,viewer_position:Vector3)->bool:
 if panel.is_open:
  panel.advance()
  return true
 var id := target(camera,viewer_position)
 if id.is_empty():return false
 if id=="Radio":radio.toggle()
 else:
  active_story=id
  var selected_story = passenger_story_provider.call() if id=="Passenger" and passenger_story_provider.is_valid() else stories[id]
  if selected_story != null: panel.open_story(selected_story)
 return true
func leave():
 panel.close_story()
 radio.reset()
func reset():
 leave()
 objects.get_node("Passenger").reset()
func caption(viewer_position:Vector3)->String:
 return radio.caption() if radio.is_on and viewer_position.distance_to(radio.global_position)<6.0 else ""

func advance_passenger(delta:float,bus_phase:String,boarding_point:Vector3):
 var passenger=objects.get_node("Passenger")
 passenger.advance(delta,bus_phase,boarding_point,panel.is_open and active_story=="Passenger")
 if panel.is_open and active_story=="Passenger" and not passenger.is_available():panel.close_story()
