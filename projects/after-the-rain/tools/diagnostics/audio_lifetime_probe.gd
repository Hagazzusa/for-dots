extends SceneTree
var mode := "immediate"
var warmed := false
var voices := []
var weak_playbacks := []
var weak_streams := []
var started := 0
func _initialize():
 var args=OS.get_cmdline_user_args()
 if not args.is_empty():mode=args[0]
 if args.size()>1:warmed=args[1]=="warmed"
 call_deferred("run")
func snapshot(label:String):
 var playback_alive:=0
 var stream_alive:=0
 for w in weak_playbacks:
  if w.get_ref()!=null:playback_alive+=1
 for w in weak_streams:
  if w.get_ref()!=null:stream_alive+=1
 print(JSON.stringify({"stage":label,"us":Time.get_ticks_usec()-started,"playbacks":playback_alive,"streams":stream_alive,"mix_age":AudioServer.get_time_since_last_mix()}))
 return playback_alive+stream_alive
func run():
 started=Time.get_ticks_usec()
 for i in range(2):
  var wav=AudioStreamWAV.new()
  wav.format=AudioStreamWAV.FORMAT_16_BITS
  wav.mix_rate=22050
  wav.loop_mode=AudioStreamWAV.LOOP_FORWARD
  wav.loop_end=2205
  var data=PackedByteArray()
  data.resize(4410)
  wav.data=data
  var p=AudioStreamPlayer.new()
  p.stream=wav
  root.add_child(p)
  p.play()
  weak_playbacks.append(weakref(p.get_stream_playback()))
  weak_streams.append(weakref(wav))
  voices.append(p)
  wav=null
 snapshot("playing")
 if warmed:
  var last_mix_age:=AudioServer.get_time_since_last_mix()
  var warm_deadline:=Time.get_ticks_usec()+2000000
  var mixed:=false
  while Time.get_ticks_usec()<warm_deadline:
   await process_frame
   var age:=AudioServer.get_time_since_last_mix()
   if age<last_mix_age:
    mixed=true
    break
   last_mix_age=age
  print("OBSERVED_MIX="+str(mixed))
  snapshot("mixed")
 for p in voices:
  p.stop()
  p.stream=null
  p.queue_free()
 voices.clear()
 snapshot("stopped")
 if mode=="immediate":
  quit();return
 # Observe real releases at frame boundaries, bounded diagnosis rather than a fixed sleep.
 var deadline=Time.get_ticks_usec()+2000000
 var frames:=0
 while Time.get_ticks_usec()<deadline:
  await process_frame
  frames+=1
  if snapshot("frame_%d"%frames)==0:
   print("RELEASED")
   quit();return
 print("DEADLINE_NOT_RELEASED")
 quit(2)
