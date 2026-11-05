extends SceneTree
var checks:=0
var failures:=0
func check(value:bool,label:String):
 checks+=1
 print("REFUGE SIGN ","PASS " if value else "FAIL ",label)
 if not value:failures+=1
func _initialize():call_deferred("run")
func run():
 var scene=load("res://scenes/neighborhood_extension.tscn")
 var a=scene.instantiate();var b=scene.instantiate()
 root.add_child(a);root.add_child(b)
 var sign:Label3D=a.get_node("RefugeSign")
 check(not sign.double_sided,"saved exterior sign hides its back")
 check(sign.text=="늦은 밤에도 잠깐 쉬어 가세요" and sign.font_size==26 and is_equal_approx(sign.pixel_size,.005),"wording and size unchanged")
 check(sign.position==Vector3(7,1.4,-4.45) and sign.rotation==Vector3.ZERO,"authored front orientation and position unchanged")
 check(sign.visible and not sign.no_depth_test and sign.billboard==0,"front remains visible with normal depth test")
 check(a.get_node("Wayfinding").double_sided,"unrelated direction sign unchanged")
 sign.double_sided=true
 check(not b.get_node("RefugeSign").double_sided,"node-local property isolates instances")
 a.reset();b.reset()
 check(not b.get_node("RefugeSign").double_sided,"new-night reset preserves backface setting")
 a.free();b.free()
 var c=scene.instantiate();root.add_child(c)
 check(not c.get_node("RefugeSign").double_sided,"fresh instance retains saved setting")
 c.free()
 print("REFUGE SIGN ",checks," checks, ",failures," failures")
 quit(1 if failures else 0)
