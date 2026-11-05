extends RefCounted
## Capture weak playback references BEFORE stopping. Cached WAV lifetime is irrelevant.
static func stop_player(player: Node) -> Array[WeakRef]:
 var pending: Array[WeakRef]=[]
 if not is_instance_valid(player):return pending
 if player.has_stream_playback():pending.append(weakref(player.get_stream_playback()))
 player.stop()
 player.stream=null
 # 3D players retain a pending-playback reference until the node is destroyed.
 player.queue_free()
 return pending
