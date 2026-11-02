extends Node3D
## Sheltered cat: weather hysteresis and optional blink, no automatic processing.
signal caption_requested(text: String)
@export var travel_seconds := 2.8
@export var greeting_seconds := 2.4
@onready var visual: Node3D = $Visual
@onready var rest_anchor: Marker3D = $RestAnchor
@onready var peek_anchor: Marker3D = $PeekAnchor
@onready var eyes: Node3D = $Visual/Head/Eyes
@onready var interaction: Marker3D = $Interaction
@onready var tail: Node3D = $Visual/Tail
var emergence := 0.0
var wants_out := false
var greeted := false
var greeting_elapsed := 0.0
var greeting_active := false
var phase := 0.0

func reset() -> void:
	emergence = 0.0
	wants_out = false
	greeted = false
	greeting_active = false
	greeting_elapsed = 0.0
	phase = 0.0
	_present()

func _ready() -> void: reset()

func can_greet() -> bool:
	return wants_out and emergence >= 0.999 and not greeted

func request_greeting() -> bool:
	if not can_greet(): return false
	greeted = true
	greeting_active = true
	greeting_elapsed = 0.0
	caption_requested.emit("고양이가 눈을 천천히 감았다 뜬다.")
	return true

func advance(delta: float, lull_strength: float) -> void:
	if not is_finite(delta) or not is_finite(lull_strength): return
	var dt := maxf(delta,0.0)
	if lull_strength > 0.7: wants_out = true
	elif lull_strength < 0.3: wants_out = false
	emergence = move_toward(emergence,1.0 if wants_out else 0.0,dt/maxf(travel_seconds,0.01))
	if not wants_out and emergence == 0.0:
		greeted = false
		greeting_active = false
		greeting_elapsed = 0.0
	if greeting_active:
		greeting_elapsed = minf(greeting_elapsed+dt,maxf(greeting_seconds,0.01))
		if greeting_elapsed >= maxf(greeting_seconds,0.01): greeting_active = false
	phase = fposmod(phase+dt*0.8,TAU)
	_present()

func _present() -> void:
	visual.position = rest_anchor.position.lerp(peek_anchor.position,smoothstep(0.0,1.0,emergence))
	interaction.position = visual.position+Vector3(0,0.27,0.18)
	tail.rotation.z = sin(phase)*0.06
	var blink := 0.0
	if greeting_active:
		blink = pow(sin(PI*clampf(greeting_elapsed/maxf(greeting_seconds,0.01),0.0,1.0)),4.0)
	eyes.scale.y = lerpf(1.0,0.08,blink)
