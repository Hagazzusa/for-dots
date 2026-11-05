extends RefCounted
static func attach(host:Node) -> void:
	host.get_window().title = "TEST ONLY — visual fixture (not ordinary play)"
	var layer=CanvasLayer.new()
	layer.layer=120
	var label=Label.new()
	label.add_theme_font_override("font",load("res://assets/fonts/NotoSansCJK-Regular.ttc"))
	label.text="TEST ONLY — 일반 플레이 아님"
	label.position=Vector2(20,110)
	label.add_theme_font_size_override("font_size",22)
	label.add_theme_color_override("font_color",Color(1,.25,.1))
	layer.add_child(label)
	host.add_child(layer)
