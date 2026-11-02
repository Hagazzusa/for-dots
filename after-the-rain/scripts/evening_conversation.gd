extends Node
## Optional second conversation. Reader identity is the transaction token;
## resources are never mutated, and this component never opens a reader itself.
const StoryText = preload("res://config/story_text.gd")
@export var question_story: StoryText = preload("res://config/story_reason_question.tres")
@export var work_story: StoryText = preload("res://config/story_reason_work.tres")
@export var walk_story: StoryText = preload("res://config/story_reason_walk.tres")
var has_met := false
var reason := ""
var _panel: Node
var _passenger: Node
var _greeting: Resource
var _greeting_pending: Resource
var _question_pending: Resource

func initialize(panel: Node, original_greeting: Resource, passenger: Node) -> void:
	_detach()
	has_met = false
	reason = ""
	_panel = panel
	_passenger = passenger
	_greeting = original_greeting
	_panel.story_closed.connect(_on_story_closed)
	_panel.choice_selected.connect(_on_choice)

func _available() -> bool:
	return is_instance_valid(_panel) and is_instance_valid(_passenger) and _passenger.is_available()

func next_story() -> Resource:
	_invalidate(false)
	if not _available(): return null
	if not has_met:
		_greeting_pending = _greeting
		return _greeting
	if reason == "work": return work_story
	if reason == "walk": return walk_story
	# Unique immutable reader instance: an old popup cannot own a later choice.
	_question_pending = question_story.duplicate() as Resource
	return _question_pending

func prompt_text() -> String:
	if not has_met: return "[E] 비를 피하는 승객에게 인사하기"
	if reason.is_empty(): return "[E] 승객과 조금 더 이야기하기"
	return "[E] 승객에게 다시 말 걸기"

func ride_memory() -> String:
	match reason:
		"work": return "일을 마치고 돌아가는 길. 이제 조금 앉아 있어도 되겠다."
		"walk": return "그냥 걷다가 탄 버스. 창밖으로 아까 지나온 길이 흐른다."
	return ""

func _on_choice(index: int) -> void:
	if _question_pending == null: return
	if not _available() or not _panel.is_open or _panel.current_story != _question_pending:
		_invalidate(false)
		return
	if index not in [0,1]: return
	reason = "work" if index == 0 else "walk"
	_question_pending = null

func _on_story_closed(story: Resource) -> void:
	if _greeting_pending != null and story == _greeting_pending and _available():
		has_met = true
	_invalidate(false)

func _process(_delta: float) -> void:
	if _greeting_pending == null and _question_pending == null: return
	if not _available():
		_invalidate(true)
	elif not _panel.is_open or (_panel.current_story != _greeting_pending and _panel.current_story != _question_pending):
		_invalidate(false)

func _invalidate(close_owned: bool) -> void:
	var should_close := false
	if close_owned and is_instance_valid(_panel) and _panel.is_open:
		should_close = (_greeting_pending != null and _panel.current_story == _greeting_pending) or (_question_pending != null and _panel.current_story == _question_pending)
	_greeting_pending = null
	_question_pending = null
	if should_close: _panel.close_story()

func reset() -> void:
	_invalidate(true)
	has_met = false
	reason = ""

func _detach() -> void:
	_invalidate(true)
	if is_instance_valid(_panel):
		if _panel.story_closed.is_connected(_on_story_closed): _panel.story_closed.disconnect(_on_story_closed)
		if _panel.choice_selected.is_connected(_on_choice): _panel.choice_selected.disconnect(_on_choice)

func _exit_tree() -> void:
	_detach()
