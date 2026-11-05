extends SceneTree
var failures := 0
var checks := 0
func check(ok: bool, label: String) -> void:
 checks += 1
 if not ok:
  failures += 1
  push_error(label)
func _initialize() -> void: call_deferred("run")
func run() -> void:
 var scene = load("res://scenes/flower_life.tscn")
 var a = scene.instantiate()
 var b = scene.instantiate()
 root.add_child(a); root.add_child(b)
 await process_frame
 var marker: Transform3D = a.get_node("Interaction").transform
 var fold_rest: Transform3D = a.paper_fold.transform
 var arm_rest: Transform3D = a.work_arm.transform
 check(a.get_node("PreparedBouquet").find_children("*","MeshInstance3D",true,false).size()==4,"four authored static bouquet meshes")
 a.advance(a.dwell_seconds+a.work_seconds*.55,Vector3(0,0,2))
 check(a.state=="work" and a.work_arm.rotation.z<-.8 and a.paper_fold.rotation.z<-.15,"one visible reach and paper press")
 var hand:Vector3=a.to_local(a.work_arm.get_node("Hand").global_position)
 var paper:Vector3=a.to_local(a.paper_fold.global_position)
 check(absf(hand.x-paper.x)<.10 and absf(hand.y-(paper.y+.10))<.04 and absf(hand.z-paper.z)<.012,"hand reaches paper upper edge")
 check(b.state=="idle" and b.paper_fold.transform==fold_rest,"two instances independent")
 check(not a.request_wave(),"work does not steal established wave eligibility")
 a.advance(a.work_seconds*.45,Vector3(0,0,2))
 check(a.can_wave() and a.work_arm.transform.is_equal_approx(arm_rest) and a.paper_fold.transform.is_equal_approx(fold_rest),"window restores work poses")
 check(a.request_wave(),"wave still accepted")
 a.advance(1.2,Vector3(0,0,2))
 check(a.arm.rotation.z>.5 and a.work_arm.transform.is_equal_approx(arm_rest),"wave uses other arm")
 a.reset()
 check(a.work_arm.transform.is_equal_approx(arm_rest) and a.paper_fold.transform.is_equal_approx(fold_rest),"reset during gesture restores authored pose")
 for visit in range(40):
  a.advance(1e3,Vector3(0,0,2))
  check(a.state=="done" and a.paper_fold.transform.is_equal_approx(fold_rest),"no residual pose after visit")
  a.advance(0,Vector3(5,0,0))
 check(a.get_node("Interaction").transform==marker and a.work_arm.transform.is_equal_approx(arm_rest),"repeat visits no marker/arm drift")
 a.advance(a.dwell_seconds+1.7,Vector3(0,0,2))
 a.reset()
 check(a.paper_fold.transform.is_equal_approx(fold_rest),"reset mid press")
 var packed := PackedScene.new()
 check(packed.pack(a)==OK,"pack actor and bouquet")
 var save_path := "user://flower_wrapping_saved.tscn"
 check(ResourceSaver.save(packed,save_path)==OK,"save authored bouquet scene")
 var reopened=ResourceLoader.load(save_path,"",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
 root.add_child(reopened)
 check(reopened.get_node("PreparedBouquet").find_children("*","MeshInstance3D",true,false).size()==4,"authored bouquet survives packing")
 reopened.free()
 DirAccess.remove_absolute(ProjectSettings.globalize_path(save_path))
 a.free(); b.free()
 await process_frame
 print("FLOWER WRAPPING: %d checks / %d failures"%[checks,failures])
 quit(1 if failures else 0)
