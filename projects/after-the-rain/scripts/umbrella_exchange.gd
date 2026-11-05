extends Node
## Explicit optional loan. Root owns targeting and shared basket visibility.
signal lent
const StoryText = preload("res://config/story_text.gd")
@export var offer_text: StoryText = preload("res://config/story_loan_offer.tres")
var loaned := false
var departed := false
var offering := false
var _owns_reader := false
var _thanks_pending := false
var umbrella: Node3D
var passenger: Node3D
var panel: CanvasLayer
@onready var loan_prop: Node3D = $LoanProp
var _old_prop_visibility: Dictionary = {}

func initialize(held_umbrella: Node3D, person: Node3D, reader: CanvasLayer) -> void:
	_thanks_pending = false
	_restore_old_prop()
	_disconnect_reader()
	umbrella = held_umbrella
	passenger = person
	panel = reader
	offering = false
	_owns_reader = false
	if is_instance_valid(panel):
		panel.choice_selected.connect(_on_choice)
		panel.story_closed.connect(_on_story_closed)
	_present_prop()

func _disconnect_reader() -> void:
	if not is_instance_valid(panel): return
	if panel.choice_selected.is_connected(_on_choice): panel.choice_selected.disconnect(_on_choice)
	if panel.story_closed.is_connected(_on_story_closed): panel.story_closed.disconnect(_on_story_closed)

func can_offer() -> bool:
	return is_instance_valid(umbrella) and is_instance_valid(passenger) and is_instance_valid(panel) and not loaned and umbrella.held and passenger.is_available() and not panel.is_open

func request_offer() -> bool:
	if not can_offer(): return false
	offering = true
	_owns_reader = true
	panel.open_story(offer_text)
	if not panel.is_open or panel.current_story != offer_text:
		offering = false
		_owns_reader = false
	return offering

func _reader_matches() -> bool:
	return _owns_reader and is_instance_valid(panel) and panel.is_open and panel.current_story == offer_text

func _on_choice(index: int) -> void:
	if not offering: return
	if not _reader_matches():
		offering = false
		_owns_reader = false
		return
	if index < 0 or index > 1: return
	offering = false
	if index == 1: return
	if loaned or not is_instance_valid(umbrella) or not umbrella.held or not is_instance_valid(passenger) or not passenger.is_available():
		_owns_reader = false
		panel.close_story()
		return
	# Commit ownership before return_umbrella emits state_changed, so basket
	# listeners never observe a returned item that is simultaneously lent.
	loaned = true
	_thanks_pending = true
	umbrella.return_umbrella()
	_present_prop()
	lent.emit()

func _on_story_closed(story: Resource) -> void:
	var nod: bool = _thanks_pending and _owns_reader and story == offer_text and is_instance_valid(passenger) and passenger.is_available()
	_thanks_pending = false
	offering = false
	_owns_reader = false
	if nod: passenger.request_thanks()

func present(_delta: float, bus_phase: String = "") -> void:
	if _thanks_pending and not _reader_matches(): _thanks_pending = false
	if loaned and is_instance_valid(passenger) and passenger.state == "boarded" and bus_phase == "departing":
		departed = true
	_present_prop()
	if not offering: return
	if not _reader_matches():
		offering = false
		_owns_reader = false
	elif not is_instance_valid(umbrella) or not umbrella.held or not is_instance_valid(passenger) or not passenger.is_available():
		offering = false
		_owns_reader = false
		panel.close_story()

func reset() -> void:
	var close_owned: bool = _reader_matches()
	_thanks_pending = false
	offering = false
	_owns_reader = false
	loaned = false
	departed = false
	_present_prop()
	if close_owned: panel.close_story()

func boarding_caption(actual_companion: bool) -> String:
	if not loaned: return ""
	if actual_companion and not departed:
		return "가까운 자리에서 작은 목소리. “우산은 다음 비 오는 날, 그 자리에 둘게요.”"
	return "‘다음 비 오는 날, 그 자리에.’ 빌려준 우산과 짧은 약속이 떠오른다."

func _present_prop() -> void:
	if not is_instance_valid(loan_prop): return
	loan_prop.visible = loaned and not departed and is_instance_valid(passenger) and passenger.visible
	if not is_instance_valid(passenger): return
	var visual: Node3D = passenger.visual
	if loan_prop.visible:
		loan_prop.global_transform = visual.global_transform * Transform3D(Basis.IDENTITY,Vector3(-0.245,0.675,0.015))
	# This story's passenger has no umbrella until the explicit shared loan.
	# Suppress the V7 prototype prop for this binding, restoring only on release.
	for child_name in ["ClosedUmbrella","UmbrellaHandle"]:
		var old_prop: Node3D = visual.get_node_or_null(child_name)
		if old_prop != null:
			if not _old_prop_visibility.has(old_prop): _old_prop_visibility[old_prop]=old_prop.visible
			old_prop.visible=false

func _restore_old_prop() -> void:
	for old_prop in _old_prop_visibility:
		if is_instance_valid(old_prop): old_prop.visible=_old_prop_visibility[old_prop]
	_old_prop_visibility.clear()

func _exit_tree() -> void:
	_restore_old_prop()
	_disconnect_reader()
