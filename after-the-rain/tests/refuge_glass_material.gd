extends SceneTree
var failures := 0
var checks := 0
func check(value: bool, label: String) -> void:
 checks += 1
 print("GLASS ", "PASS " if value else "FAIL ", label)
 if not value: failures += 1
func _initialize(): call_deferred("run")
func run():
 var packed = load("res://scenes/neighborhood_extension.tscn") as PackedScene
 var template = load("res://config/refuge_glass.tres") as StandardMaterial3D
 var a = packed.instantiate()
 var b = packed.instantiate()
 var aw = a.get_node("GlassRefuge")
 var bw = b.get_node("GlassRefuge")
 check(aw.glass_material != null, "saved Inspector template before ready")
 root.add_child(a); root.add_child(b)
 await process_frame
 check(aw.panes.size() == 24 and bw.panes.size() == 24, "24 panes in each instance")
 var ids := {}
 for pane in aw.panes + bw.panes:
  var mat = pane.material_override as StandardMaterial3D
  check(mat != null and mat != template, "pane duplicate not template")
  check(not ids.has(mat.get_instance_id()), "unique pane material identity")
  ids[mat.get_instance_id()] = true
  check(mat.albedo_color.is_equal_approx(Color(.55,.74,.82,.14)) and is_equal_approx(mat.roughness,.1) and is_equal_approx(mat.metallic,.05), "baseline color roughness metallic")
  check(mat.transparency == BaseMaterial3D.TRANSPARENCY_ALPHA and mat.cull_mode == BaseMaterial3D.CULL_DISABLED and mat.resource_local_to_scene and pane.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "baseline alpha culling local shadow")
 var color = aw.panes[0].material_override.albedo_color
 aw.panes[0].material_override.albedo_color = Color.RED
 check(aw.panes[1].material_override.albedo_color.is_equal_approx(color) and bw.panes[0].material_override.albedo_color.is_equal_approx(color), "pane and instance mutation isolated")
 check(template.albedo_color.is_equal_approx(color) and aw.glass_material.albedo_color.is_equal_approx(color), "template immutable")
 aw.set_glass_visible(false)
 check(not aw.panes[0].visible and bw.panes[0].visible, "visibility remains instance local")
 var c = packed.instantiate()
 var cw = c.get_node("GlassRefuge")
 cw.glass_material = null
 root.add_child(c)
 check(cw.panes[0].material_override.albedo_color.is_equal_approx(color), "null Inspector setting uses default")
 var d = packed.instantiate()
 var dw = d.get_node("GlassRefuge")
 var custom = template.duplicate() as StandardMaterial3D
 custom.roughness = .3
 dw.glass_material = custom
 root.add_child(d)
 check(is_equal_approx(dw.panes[0].material_override.roughness,.3), "assigned template reaches pane")
 dw.panes[0].material_override.roughness = .8
 check(is_equal_approx(custom.roughness,.3) and is_equal_approx(dw.panes[1].material_override.roughness,.3), "custom template remains immutable")
 a.queue_free(); b.queue_free(); c.queue_free(); d.queue_free()
 await process_frame
 var fresh = packed.instantiate()
 root.add_child(fresh)
 check(fresh.get_node("GlassRefuge").panes[0].material_override.albedo_color.is_equal_approx(color), "fresh instance after free has defaults")
 fresh.queue_free()
 await process_frame
 print("GLASS SUMMARY ",checks," checks ",failures," failures")
 quit(1 if failures else 0)
