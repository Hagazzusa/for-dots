extends Node
## Sole owner of cup gameplay state. No presentation nodes or sibling lookups.
## Session calls request_action with explicit proximity/flow gates, then advance.
signal dispense_started
signal filled
signal sip_started
signal fill_target_changed(amount: float, immediate: bool)
signal note_requested(text: String, duration: float)

@export_range(0.1, 10.0, 0.1) var dispense_seconds := 1.2
@export_range(0.1, 10.0, 0.1) var sip_seconds := 1.3
@export_range(0.0, 10.0, 0.1) var fill_change_remaining := 0.8
@export_range(1, 10, 1) var servings := 3
@export_range(1.0,600.0,1.0) var cooling_seconds := 180.0
@export_range(0.0,1.0,0.01) var minimum_heat := 0.18
var cup_age := 0.0
var sips := 0
var has_cup := false
var dispensing := 0.0
var sip_time := 0.0
var fill_pending := false

func sip_progress()->float:
	return clampf(1.0-sip_time/maxf(sip_seconds,.001),0.0,1.0) if sip_time>0.0 else -1.0
func cup_heat()->float:
	if not has_cup or sips<=0:return 0.0
	return lerpf(1.0,clampf(minimum_heat,0.0,1.0),clampf(cup_age/maxf(cooling_seconds,.001),0.0,1.0))

func request_action(can_dispense: bool, blocked: bool) -> bool:
	if blocked or dispensing > 0.0 or sip_time > 0.0:
		return false
	if sips > 0:
		sips -= 1
		sip_time = sip_seconds
		fill_pending = true
		sip_started.emit()
		note_requested.emit("Warm hands. A small sweetness." if sips>0 else "The last sip. A little warmer now.", 5.0)
		return true
	if can_dispense:
		dispensing = dispense_seconds
		note_requested.emit("A cup drops into the tray.", 3.0)
		dispense_started.emit()
		return true
	return false

func advance(delta: float) -> void:
	if not is_finite(delta):return
	delta=maxf(delta,0.0)
	if has_cup and sips>0:cup_age=minf(cup_age+delta,maxf(cooling_seconds,.001))
	# Keep v3 update order: dispense completion, sip countdown, delayed fill target.
	if dispensing > 0.0:
		dispensing -= delta
		if dispensing <= 0.0:
			sips = servings
			has_cup = true
			cup_age = 0.0
			fill_target_changed.emit(1.0, true)
			filled.emit()
			note_requested.emit("Hot cocoa. Just what your hands needed.", 5.0)
	if sip_time > 0.0:
		sip_time = maxf(0.0, sip_time-delta)
	if fill_pending and sip_time <= fill_change_remaining:
		fill_target_changed.emit(float(sips)/float(servings), false)
		fill_pending = false

func reset() -> void:
	cup_age = 0.0
	sips = 0
	has_cup = false
	dispensing = 0.0
	sip_time = 0.0
	fill_pending = false
	fill_target_changed.emit(0.0, true)

func dispose_empty() -> bool:
	if not has_cup or sips != 0 or dispensing > 0.0 or sip_time > 0.0:
		return false
	reset()
	note_requested.emit("An empty cup put away. A small kindness.", 4.0)
	return true
