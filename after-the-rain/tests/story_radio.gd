extends SceneTree
func _initialize():
	call_deferred("run")
func run():
	var count_before := AudioServer.bus_count
	var orphan_before := Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	var scene = load("res://scenes/story_radio_audio.tscn")
	var a = scene.instantiate()
	var b = scene.instantiate()
	root.add_child(a)
	root.add_child(b)
	assert(not a.is_on and not a.player.playing)
	assert(a.player.stream != b.player.stream)
	assert(is_equal_approx(a.player.stream.get_length(), 16.0))
	assert(a.player.stream.loop_end == 352800)
	assert(a.player.stream.loop_mode == AudioStreamWAV.LOOP_FORWARD)
	a.toggle()
	assert(a.is_on and a.player.playing and not b.is_on and not b.player.playing)
	assert(a.caption() == "작은 라디오 · 느린 건반 선율")
	a.set_muted(true)
	assert(a.player.volume_db == -80.0 and b.player.volume_db == -23.0)
	a.set_muted(false)
	assert(a.player.volume_db == -23.0)
	assert(a.player.bus == &"Master" and a.player.max_distance == 6.0)
	a.player.seek(15.9)
	await create_timer(.3).timeout
	assert(a.player.playing)
	a.toggle()
	assert(not a.is_on and not a.player.playing)
	b.toggle()
	b.reset()
	assert(not b.is_on and not b.player.playing)
	a.toggle()
	a.queue_free()
	b.queue_free()
	await process_frame
	await process_frame
	await create_timer(.2).timeout
	assert(AudioServer.bus_count == count_before)
	assert(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT) == orphan_before)
	print("STORY RADIO PASS: original 16s loop, two-instance playback/mute independence, toggle/reset/free, Master routing, no extra buses/orphans")
	quit()
