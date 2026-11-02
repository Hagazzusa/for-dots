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
	assert(a.player.stream.format == AudioStreamWAV.FORMAT_16_BITS)
	assert(a.player.stream.mix_rate == 22050 and not a.player.stream.stereo)
	assert(is_equal_approx(a.player.stream.get_length(), 48.0))
	assert(a.player.stream.loop_end == 1058400)
	assert(a.player.stream.loop_mode == AudioStreamWAV.LOOP_FORWARD)
	for position in [0.0, 15.99, 16.0, 31.99, 32.0, 47.99, 48.0, 64.0, 96.0]:
		var expected := int(fposmod(position,48.0)/16.0)
		assert(a.caption_for_position(position) == a.PHRASE_CAPTIONS[expected])
	a.toggle()
	assert(a.is_on and a.player.playing and not b.is_on and not b.player.playing)
	await create_timer(.08).timeout
	assert(a.caption() == a.PHRASE_CAPTIONS[0])
	a.player.seek(17.0)
	await create_timer(.08).timeout
	assert(a.caption() == a.PHRASE_CAPTIONS[1], "Caption follows real seek, not scene clock")
	a.player.seek(33.0)
	await create_timer(.08).timeout
	assert(a.caption() == a.PHRASE_CAPTIONS[2])
	a.set_muted(true)
	assert(a.player.volume_db == -80.0 and b.player.volume_db == -23.0)
	assert(a.player.playing and a.caption() == a.PHRASE_CAPTIONS[2], "Mute preserves playback/caption")
	a.set_muted(false)
	assert(a.player.volume_db == -23.0)
	assert(a.player.bus == &"Master" and a.player.max_distance == 6.0)
	paused = true
	await create_timer(.05, true).timeout
	var frozen: float = a.playback_seconds()
	var frozen_caption: String = a.caption()
	await create_timer(.2, true).timeout
	assert(absf(a.playback_seconds()-frozen)<.06 and a.caption()==frozen_caption, "Pause freezes real audio position")
	paused = false
	a.player.seek(47.9)
	await create_timer(.4).timeout
	assert(a.player.playing and a.playback_seconds()<1.0 and a.caption()==a.PHRASE_CAPTIONS[0], "Loop returns caption to phrase one")
	a.toggle()
	assert(not a.is_on and not a.player.playing and a.playback_seconds()==0.0)
	assert(a.caption()=="작은 라디오 · 꺼져 있음")
	b.toggle()
	b.reset()
	assert(not b.is_on and not b.player.playing)
	a.toggle()
	await create_timer(.06).timeout
	assert(a.caption()==a.PHRASE_CAPTIONS[0], "Toggle on restarts first phrase")
	a.queue_free()
	b.queue_free()
	await process_frame
	await process_frame
	await create_timer(.2).timeout
	assert(AudioServer.bus_count == count_before)
	assert(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT) == orphan_before)
	print("STORY RADIO PASS: 48s PCM loop, playback captions/seek/pause, private playback/mute, toggle/reset/free, no buses/orphans")
	quit()
