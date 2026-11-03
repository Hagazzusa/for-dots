extends Node3D
## Read-only wrapper around the imported derivative. Visibility is local instance state.
signal glass_changed(visible_now: bool)
const DEFAULT_GLASS: StandardMaterial3D = preload("res://config/refuge_glass.tres")
## Inspector-editable template; each pane receives its own runtime copy.
@export var glass_material: StandardMaterial3D = DEFAULT_GLASS
var glass_visible := true
var panes: Array[MeshInstance3D] = []
var globe: MeshInstance3D

func _ready() -> void:
	for node in $Imported.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if str(mesh.name).begins_with("GlassPane"):
			panes.append(mesh)
			var template := glass_material if glass_material != null else DEFAULT_GLASS
			var glass := template.duplicate() as StandardMaterial3D
			glass.resource_local_to_scene = true
			mesh.material_override = glass
			mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif str(mesh.name).begins_with("PendantGlobe"):
			globe = mesh

func set_glass_visible(value: bool) -> void:
	glass_visible = value
	for pane in panes:
		pane.visible = value
	glass_changed.emit(value)
