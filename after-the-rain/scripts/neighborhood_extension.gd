extends Node3D
## Optional public-space observations. Session injects its reader; no bus or player ownership.
@export var observation_radius := 2.5
@export var facing_threshold := 0.75
@export var seat_radius := 1.8
@export var seat_facing_threshold := 0.68
@onready var cover = $GlassRefuge/RainCover
@onready var heater: AudioStreamPlayer3D = $ParkedCar/Heater
var panel: CanvasLayer
var elapsed := 0.0
var shutting_down := false
const AudioRelease = preload("res://scripts/audio_release.gd")
var enabled := true
var car_text = preload("res://config/story_car.tres")
var refuge_text = preload("res://config/story_refuge.tres")
func initialize(reading_panel:CanvasLayer) -> void:
 panel=reading_panel
 _prepare_heater()
func _prepare_heater() -> void:
 var audio := AudioStreamWAV.new()
 audio.format=AudioStreamWAV.FORMAT_16_BITS
 audio.mix_rate=16000
 audio.loop_mode=AudioStreamWAV.LOOP_FORWARD
 audio.loop_end=16000
 var bytes := PackedByteArray()
 bytes.resize(32000)
 var rng:=RandomNumberGenerator.new()
 rng.seed=1740
 var low:=0.0
 for i in range(16000):
  low=lerpf(low,rng.randf_range(-1,1),0.06)
  var sample:=int((low*0.12+sin(TAU*80*i/16000.0)*0.008)*32767)
  bytes.encode_s16(i*2,sample)
 audio.data=bytes
 heater.stream=audio
func target(camera:Camera3D, viewer:Vector3) -> String:
 if not enabled or camera==null:return ""
 var best:=facing_threshold
 var selected:=""
 for id in ["Car","Refuge"]:
  if id=="Car" and $ParkedCar.to_local(viewer).x<1.05:continue
  var point:Vector3=get_node(id+"Observation").global_position
  var direction:Vector3=point-camera.global_position
  if viewer.distance_to(point)>observation_radius:continue
  var alignment:=(-camera.global_basis.z).dot(direction.normalized())
  if alignment>best:
   best=alignment
   selected=id
 return selected
func hint(camera:Camera3D,viewer:Vector3)->String:
 if can_sit(camera,viewer):return "[E] 유리 쉼터 벤치에 앉기"
 var id=target(camera,viewer)
 if id=="Car":return "[E] 차 밖에서 잠깐 바라보기 · 두 사람의 자리는 그대로"
 if id=="Refuge":return "[E] 유리 쉼터의 작은 안내 읽기"
 return ""
func try_interact(camera:Camera3D,viewer:Vector3)->bool:
 var id=target(camera,viewer)
 if id.is_empty() or panel==null:return false
 panel.open_story(car_text if id=="Car" else refuge_text)
 return true
func advance(delta:float)->void:
 if shutting_down or not enabled or not is_finite(delta):return
 if heater.stream and not heater.playing:heater.play()
 elapsed+=maxf(delta,0.0)
 # Tiny seated breathing, not conversation, driving or a new occupant.
 $ParkedCar/Driver.position.y=sin(elapsed*1.05)*0.003
 $ParkedCar/Passenger.position.y=sin(elapsed*0.92+0.8)*0.003
func set_active(value:bool)->void:
 enabled=value
 if not value:heater.stop()
func reset()->void:
 if shutting_down:return
 elapsed=0.0
 enabled=true
 $ParkedCar/Driver.position.y=0
 $ParkedCar/Passenger.position.y=0
 heater.stream_paused=false

func shutdown()->void:
 if is_instance_valid(heater):
  heater.stop()
  heater.stream=null

func _exit_tree()->void:
 shutdown()

func seat_position()->Vector3:
 return $GlassRefuge/RestSeat/Sit.global_position
func stand_position()->Vector3:
 return $GlassRefuge/RestSeat/Stand.global_position
func can_sit(camera:Camera3D,viewer:Vector3)->bool:
 if not enabled or camera==null:return false
 # Only approach from the actual interior/front, never through the rear glazing.
 var local_view:Vector3=$GlassRefuge.to_local(viewer)
 if local_view.z < -0.55 or absf(local_view.x)>1.3:return false
 var point:Vector3=$GlassRefuge/RestSeat/Interaction.global_position
 return viewer.distance_to(point)<seat_radius and (-camera.global_basis.z).dot((point-camera.global_position).normalized())>seat_facing_threshold


func begin_shutdown() -> Array[WeakRef]:
 if shutting_down:return []
 shutting_down=true
 enabled=false
 return AudioRelease.stop_player(heater)
