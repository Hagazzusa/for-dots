extends SceneTree
var closed_count = 0
var choice_count = 0
func _initialize(): call_deferred("run")
func on_closed(): closed_count += 1
func on_choice(_index): choice_count += 1
func run():
	var scene = load("res://scenes/story_panel.tscn")
	var a = scene.instantiate()
	var b = scene.instantiate()
	root.add_child(a)
	root.add_child(b)
	a.closed.connect(on_closed)
	a.choice_selected.connect(on_choice)
	var passenger = load("res://config/story_passenger.tres")
	var original = passenger.pages.duplicate()
	assert(not a.is_open and not b.is_open)
	a.open_story(passenger)
	b.open_story(passenger)
	a.advance()
	assert(a.is_open and a._awaiting_choice)
	a.select_choice(0)
	assert(not a._awaiting_choice and b._awaiting_choice)
	assert(passenger.pages == original and a._pages != b._pages)
	a.advance()
	a.close_story()
	assert(closed_count == 1 and choice_count == 1 and not a.is_open)
	a.open_story(passenger)
	a.select_choice(1)
	assert(choice_count == 2 and a.body_label.text == passenger.choice_responses[1])
	a.close_story()
	for path in ["res://config/story_memo.tres","res://config/story_route.tres"]:
		var story = load(path)
		a.open_story(story)
		assert(a._page == 0 and a.is_open)
		a.advance()
		assert(a._page == 1 and a.is_open)
		a.advance()
		assert(not a.is_open)
	assert(closed_count == 4)
	for story_path in ["res://config/story_memo.tres","res://config/story_route.tres","res://config/story_passenger.tres"]:
		var story = load(story_path)
		var texts = story.pages + story.choice_responses
		for text in texts:
			a.body_label.text = text
			await process_frame
			assert(a.body_label.get_minimum_size().y < 202, "Body text exceeds available area")
			print(story_path, " body minimum height ", a.body_label.get_minimum_size().y)
	a.queue_free()
	b.queue_free()
	await process_frame
	print("STORY PANEL PASS: immutable shared resources, independent open/choice/page state, repeat open, debounce close signal, memo/route flow, Korean text fits")
	quit()
