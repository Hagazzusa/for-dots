extends CanvasLayer
## Explicit local pause ownership. Never auto-pauses on focus changes.
signal restart_requested
signal mute_requested
var active := false
var _owns_pause := false
var _cursor_before := Input.MOUSE_MODE_VISIBLE
var _reading_scroll := false
var _focus_pending := false
@onready var root_control: Control = $Root
@onready var shade: ColorRect = $Root/Shade
@onready var panel: PanelContainer = $Root/Panel
@onready var hint: PanelContainer = $Root/Hint
@onready var scroll: ScrollContainer = $Root/Panel/Padding/Scroll
@onready var content: VBoxContainer = $Root/Panel/Padding/Scroll/Content
@onready var resume_button: Button = $Root/Panel/Padding/Scroll/Content/Resume
@onready var restart_button: Button = $Root/Panel/Padding/Scroll/Content/Restart

func _ready() -> void:
	resume_button.pressed.connect(resume_game)
	restart_button.pressed.connect(new_evening)
	get_viewport().size_changed.connect(_queue_layout)
	get_viewport().gui_focus_changed.connect(_on_focus_changed)
	_queue_layout()
	_present()

func pause_game() -> bool:
	if active or get_tree().paused: return false
	_cursor_before = Input.mouse_mode
	_owns_pause = true
	active = true
	get_tree().paused = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_reading_scroll = false
	_present()
	resume_button.grab_focus()
	_queue_focus()
	return true

func resume_game() -> void:
	if not _owns_pause: return
	get_tree().paused = false
	_owns_pause = false
	active = false
	Input.mouse_mode = _cursor_before
	_present()

func reset() -> void:
	resume_game()
	active = false
	_reading_scroll = false
	_present()

func new_evening() -> void:
	if not active or not _owns_pause: return
	resume_game()
	restart_requested.emit()

func _present() -> void:
	shade.visible = active
	panel.visible = active
	hint.visible = not active

func _input(event: InputEvent) -> void:
	if active and event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_WHEEL_UP,MOUSE_BUTTON_WHEEL_DOWN]:
		_reading_scroll = true
	if not event is InputEventKey or not event.pressed or event.echo: return
	if not active:
		if event.keycode == KEY_SPACE and not get_tree().paused:
			get_viewport().set_input_as_handled()
			pause_game()
		return
	if event.keycode in [KEY_TAB,KEY_ENTER,KEY_KP_ENTER,KEY_UP,KEY_DOWN,KEY_LEFT,KEY_RIGHT]:
		_reading_scroll = false
		return
	# Consume BEFORE releasing pause, preventing this key reaching gameplay.
	get_viewport().set_input_as_handled()
	match event.keycode:
		KEY_SPACE, KEY_E: resume_game()
		KEY_R: new_evening()
		KEY_M: mute_requested.emit()
		KEY_ESCAPE: Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		KEY_HOME:
			_reading_scroll = true
			scroll.scroll_vertical = 0
		KEY_END:
			_reading_scroll = true
			scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
		KEY_PAGEUP:
			_reading_scroll = true
			scroll.scroll_vertical -= int(scroll.size.y * 0.8)
		KEY_PAGEDOWN:
			_reading_scroll = true
			scroll.scroll_vertical += int(scroll.size.y * 0.8)

func _queue_layout() -> void:
	_update_layout.call_deferred()

func _update_layout() -> void:
	if not is_inside_tree(): return
	var viewport_size := get_viewport().get_visible_rect().size
	var stretch := get_viewport().get_stretch_transform().get_scale().abs()
	var scale_factor := maxf(0.05,minf(stretch.x,stretch.y))
	var width := minf(viewport_size.x-24.0,maxf(760.0,600.0/scale_factor))
	panel.offset_left = (viewport_size.x-width)*0.5
	panel.offset_right = -panel.offset_left
	panel.offset_top = minf(80.0,viewport_size.y*0.12)
	panel.offset_bottom = -minf(30.0,viewport_size.y*0.06)
	var fonts := {"Title":26,"Description":17,"Guide":17,"Resume":18,"Restart":18,"Footer":15}
	for node_name in fonts:
		var node: Control = content.get_node(node_name)
		var floor_size := 18.0 if node_name=="Title" else (12.0 if node_name=="Footer" else 14.0)
		node.add_theme_font_size_override("font_size",maxi(fonts[node_name],int(ceil(floor_size/scale_factor))))
	resume_button.custom_minimum_size.y = maxf(44.0,34.0/scale_factor)
	restart_button.custom_minimum_size.y = resume_button.custom_minimum_size.y
	hint.offset_left = -minf(150.0,(viewport_size.x-24.0)*0.5)
	hint.offset_right = -hint.offset_left
	hint.offset_top = 92.0 if viewport_size.x<960.0 else 12.0
	hint.offset_bottom = hint.offset_top+36.0
	_queue_focus()

func _on_focus_changed(control: Control) -> void:
	if active and control != null and scroll.is_ancestor_of(control):
		_reading_scroll = false
		_queue_focus()

func _queue_focus() -> void:
	if not active or _focus_pending: return
	_focus_pending = true
	get_tree().process_frame.connect(_reveal_focus,CONNECT_ONE_SHOT)

func _reveal_focus() -> void:
	_focus_pending = false
	if not active or _reading_scroll: return
	var focused := get_viewport().gui_get_focus_owner()
	if focused != null and scroll.is_ancestor_of(focused): scroll.ensure_control_visible(focused)

func _exit_tree() -> void:
	if _owns_pause:
		get_tree().paused = false
		Input.mouse_mode = _cursor_before
		_owns_pause = false
