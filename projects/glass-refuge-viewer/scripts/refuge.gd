extends Node3D
## Read-only wrapper around the imported derivative. Visibility is local instance state.
signal glass_changed(visible_now: bool)
var glass_visible := true
var panes: Array[MeshInstance3D] = []
var globe: MeshInstance3D

func _ready() -> void:
	for node in $Imported.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if str(mesh.name).begins_with("GlassPane"):
			panes.append(mesh)
			var glass := StandardMaterial3D.new()
			glass.resource_local_to_scene = true
			glass.albedo_color = Color(0.55, 0.74, 0.82, 0.14)
			glass.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			glass.roughness = 0.10
			glass.metallic = 0.05
			glass.cull_mode = BaseMaterial3D.CULL_DISABLED
			mesh.material_override = glass
			mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif str(mesh.name).begins_with("PendantGlobe"):
			globe = mesh

func set_glass_visible(value: bool) -> void:
	glass_visible = value
	for pane in panes:
		pane.visible = value
	glass_changed.emit(value)
