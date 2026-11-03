extends Node3D
## Optional, explicitly stepped visit. viewer_local_position is in this scene's space.
signal caption_requested(text: String)
@export var dwell_seconds := 1.8
@export var work_seconds := 3.2
@export var window_seconds := 12.0
@export var wave_seconds := 2.5
@export var leave_seconds := 1.8
@export var notice_radius := 3.2
@export var rearm_radius := 4.2
@onready var visual: Node3D = $Visual
@onready var arm: Node3D = $Visual/WaveArm
@onready var work_arm: Node3D = $Visual/WorkArm
@onready var work_sleeve: MeshInstance3D = $Visual/WorkArm/Sleeve
@onready var work_hand: MeshInstance3D = $Visual/WorkArm/Hand
@onready var bouquet_wrap: MeshInstance3D = $PreparedBouquet/Wrapping
var _sleeve_rest: Transform3D
var _hand_rest: Transform3D
@onready var paper_fold: Node3D = $PreparedBouquet/PaperFold
@export_range(0.0, 1.4) var wrap_reach_radians := 0.9
@export_range(0.0, 0.3) var paper_press_radians := 0.18
@onready var pickup: Node3D = $FlowerPickup
@onready var head: Node3D = $Visual/Head
var state := "idle"
var elapsed := 0.0
var visit_finished := false
var waved := false
var _materials: Array[StandardMaterial3D] = []
var _colors: Array[Color] = []

func _ready() -> void:
	_sleeve_rest = work_sleeve.transform
	_hand_rest = work_hand.transform
	for mesh in visual.find_children("*","MeshInstance3D",true,false):
		var material: StandardMaterial3D = mesh.material_override.duplicate()
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mesh.material_override = material
		_materials.append(material)
		_colors.append(material.albedo_color)
	var pieces: Array[Node3D] = [$PreparedBouquet/Wrapping, $PreparedBouquet/PaperFold, $PreparedBouquet/Flowers]
	pickup.initialize(pieces)
	reset()

func reset() -> void:
	pickup.reset_night()
	reset_visit()

func reset_visit() -> void:
	state = "idle"
	elapsed = 0.0
	visit_finished = false
	waved = false
	_present()

func can_wave() -> bool:
	return state == "window" and not waved

func request_wave() -> bool:
	if not can_wave(): return false
	waved = true
	state = "wave"
	elapsed = 0.0
	caption_requested.emit("꽃집 안에서 작은 손인사가 돌아온다.")
	_present()
	return true

func advance(delta: float, viewer_local_position: Vector3, reading_flower_note := false) -> void:
	if not is_finite(delta) or not viewer_local_position.is_finite(): return
	var distance := Vector2(viewer_local_position.x,viewer_local_position.z).length()
	if pickup.active:
		pickup.advance(delta)
		_present()
		return
	if state == "done":
		if not pickup.completed and not reading_flower_note and distance <= notice_radius:
			pickup.begin()
			_present()
			return
		if distance > rearm_radius: reset_visit()
		return
	if state == "idle":
		if distance > notice_radius: return
		state = "dwell"
		elapsed = 0.0
	if state == "dwell" and distance > notice_radius:
		reset_visit()
		return
	var remaining := maxf(delta,0.0)
	# At most six finite states per visit: large injected deltas cannot loop forever.
	for transition in range(6):
		# Preserve only this visit's remaining greeting window, never the work/wave pose.
		if state == "window" and not waved and reading_flower_note and distance <= notice_radius:
			break
		var duration := _duration()
		if duration <= 0.0: break
		var step := minf(remaining,maxf(0.0,duration-elapsed))
		elapsed += step
		remaining -= step
		if elapsed + 0.0000001 < duration: break
		elapsed = 0.0
		match state:
			"dwell": state = "window" if pickup.completed else "work"
			"work": state = "window"
			"window", "wave": state = "leave"
			"leave":
				state = "done"
				visit_finished = true
		if remaining <= 0.0: break
	_present()

func _duration() -> float:
	match state:
		"dwell": return maxf(dwell_seconds,0.01)
		"work": return maxf(work_seconds,0.01)
		"window": return maxf(window_seconds,0.01)
		"wave": return maxf(wave_seconds,0.01)
		"leave": return maxf(leave_seconds,0.01)
	return 0.0

func _present() -> void:
	var opacity := 0.0
	visual.position.x = 0.0
	arm.rotation.z = 0.0
	head.rotation.z = 0.0
	work_arm.rotation.z = 0.0
	work_sleeve.transform = _sleeve_rest
	work_hand.transform = _hand_rest
	work_arm.position = Vector3(-0.205,0.92,0)
	paper_fold.rotation.z = 0.0
	if pickup.active:
		visual.position.x = -0.35
		_present_pickup_hand()
		opacity = smoothstep(0.0,0.6,pickup.elapsed)*(1.0-smoothstep(pickup.duration()-1.2,pickup.duration(),pickup.elapsed))
	elif state == "work":
		opacity = smoothstep(0.0,0.6,elapsed)
		visual.position.x = lerpf(-0.25,0.0,clampf(elapsed/maxf(work_seconds,0.01),0.0,1.0))
		# One reach, small press, then release; no independent timer or looping tween.
		var phase := clampf(elapsed/maxf(work_seconds,0.01),0.0,1.0)
		var reach := smoothstep(0.18,0.42,phase)*(1.0-smoothstep(0.72,0.96,phase))
		var press := smoothstep(0.43,0.55,phase)*(1.0-smoothstep(0.61,0.72,phase))
		work_arm.rotation.z = -wrap_reach_radians*reach
		work_arm.position.x = -0.205-visual.position.x*reach
		work_arm.position.z = 0.055*reach
		paper_fold.rotation.z = -paper_press_radians*press
		head.rotation.z = 0.07*reach
	elif state in ["window","wave"]:
		opacity = 1.0
		if state == "wave":
			var envelope := sin(PI*clampf(elapsed/maxf(wave_seconds,0.01),0.0,1.0))
			arm.rotation.z = envelope*(0.9+sin(elapsed*8.0)*0.15)
	elif state == "leave":
		var fraction := clampf(elapsed/maxf(leave_seconds,0.01),0.0,1.0)
		opacity = 1.0-smoothstep(0.0,1.0,fraction)
		visual.position.x = -0.25*fraction
	visual.visible = opacity > 0.0
	for i in range(_materials.size()):
		var color := _colors[i]
		color.a *= opacity
		_materials[i].albedo_color = color

func _present_pickup_hand() -> void:
	# A flat sleeve segment follows the wrapping, then releases only after receipt.
	# This is authored silhouette staging, not anatomical IK or paper physics.
	var release := smoothstep(pickup.approach_seconds+pickup.receive_seconds,
		pickup.approach_seconds+pickup.receive_seconds+pickup.hold_seconds,pickup.elapsed)
	var grip := visual.to_local(bouquet_wrap.to_global(Vector3(0.02,0.11,0.02)))
	var rest_tip := work_arm.position + _hand_rest.origin
	var target := grip.lerp(rest_tip,release)
	var offset := Vector2(target.x-work_arm.position.x,target.y-work_arm.position.y)
	var length := offset.length()
	work_arm.position.z = target.z
	work_arm.rotation.z = atan2(offset.x,-offset.y)
	work_hand.position = Vector3(0,-length,0)
	work_sleeve.position = Vector3(0,-length*.5,0)
	work_sleeve.scale.y = length/0.34
