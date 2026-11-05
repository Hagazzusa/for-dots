extends CanvasLayer
## Optional reading surface. No movement lock or global E interception.
const StoryText = preload("res://config/story_text.gd")
signal closed
signal story_closed(story: Resource)
var current_story: Resource
# The session supplies eligibility; this panel never queries world/player siblings.
var boarding_available: Callable
signal choice_selected(index: int)
var suspended := false
var is_open: bool = false
var _pages: Array[String] = []
var _choice_labels: Array[String] = []
var _choice_responses: Array[String] = []
var _page: int = 0
var _awaiting_choice: bool = false
@onready var panel: Panel = $Panel
@onready var title_label: Label = $Panel/Title
@onready var body_label: Label = $Panel/Body
@onready var choice_label: Label = $Panel/Choices
@onready var guide_label: Label = $Panel/Guide
@onready var page_label: Label = $Panel/Page

func set_suspended(value:bool)->void:
	suspended=value
	visible=not value

func open_story(story: StoryText) -> void:
	if story == null or story.pages.is_empty():
		return
	current_story = story
	_pages.assign(story.pages)
	_choice_labels.assign(story.choice_labels)
	_choice_responses.assign(story.choice_responses)
	_page = 0
	_awaiting_choice = _choice_labels.size() == 2 and _choice_responses.size() == 2
	title_label.text = story.title
	is_open = true
	panel.show()
	_present()

func advance() -> void:
	if not is_open or _awaiting_choice:
		return
	_page += 1
	if _page >= _pages.size():
		close_story()
	else:
		_present()

func select_choice(index: int) -> void:
	if not is_open or not _awaiting_choice or index < 0 or index >= _choice_responses.size():
		return
	_pages = [_choice_responses[index]]
	_page = 0
	_awaiting_choice = false
	_present()
	choice_selected.emit(index)

func close_story() -> void:
	if not is_open:
		return
	var closing_story := current_story
	current_story = null
	is_open = false
	_awaiting_choice = false
	panel.hide()
	closed.emit()
	story_closed.emit(closing_story)

func _present() -> void:
	body_label.text = _pages[_page]
	choice_label.text = "[1] " + _choice_labels[0] + "     [2] " + _choice_labels[1] if _awaiting_choice else ""
	_refresh_guide()
	page_label.text = "%d / %d" % [_page+1,_pages.size()]

func _process(_delta: float) -> void:
	if is_open and not suspended:
		_refresh_guide()

func _refresh_guide() -> void:
	var can_board := boarding_available.is_valid() and bool(boarding_available.call())
	var action := "1 / 2 선택" if _awaiting_choice else ("E 다음" if _page < _pages.size()-1 else "E 닫기")
	if can_board:
		action = "E 버스 타기" + (" · 1 / 2 선택" if _awaiting_choice else "")
	guide_label.text = action + "    Q 닫기 · 읽는 동안에도 시간은 흘러요"

func _unhandled_key_input(event: InputEvent) -> void:
	if suspended or not is_open or not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_Q:
			close_story()
			get_viewport().set_input_as_handled()
		KEY_1, KEY_KP_1:
			if _awaiting_choice:
				select_choice(0)
				get_viewport().set_input_as_handled()
		KEY_2, KEY_KP_2:
			if _awaiting_choice:
				select_choice(1)
				get_viewport().set_input_as_handled()
