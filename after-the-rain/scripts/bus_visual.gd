extends Node3D
## Authored two-leaf telescoping door. Recess first, then slide behind the entry.
## Reverse order on close avoids the front axle and keeps panels inside the bus.
@export var door_duration := .7
@onready var doors: Array[Node3D] = [$Doors/Left, $Doors/Right]
var door_tween: Tween
var door_open := false
const CLOSED_X := [2.475, 3.125]
const OPEN_X := [1.8, 1.8]
const CLOSED_Z := -1.18
const POCKET_Z := [-.70, -.50]

func set_door_open(value: bool):
	door_open = value
	if door_tween:
		door_tween.kill()
	door_tween = create_tween()
	# Parallel pairs are separated by a sequential phase boundary.
	for i in range(doors.size()):
		var property := "position:z" if value else "position:x"
		var target: float = POCKET_Z[i] if value else CLOSED_X[i]
		door_tween.tween_property(doors[i], property, target, door_duration * .35).set_trans(Tween.TRANS_SINE)
		if i == 0:
			door_tween.parallel()
	for i in range(doors.size()):
		var property := "position:x" if value else "position:z"
		var target: float = OPEN_X[i] if value else CLOSED_Z
		door_tween.tween_property(doors[i], property, target, door_duration * .65).set_trans(Tween.TRANS_SINE)
		if i == 0:
			door_tween.parallel()

# Runtime-only fade: cache once, duplicate only private materials, never shared meshes.
# Saved scene meshes all use BaseMaterial3D overrides; full opacity restores them.
var route_opacity := 1.0
var _fade_meshes: Array[Dictionary] = []
var _fade_labels: Array[Dictionary] = []
var _fade_lights: Array[Dictionary] = []

func _ready() -> void:
	_cache_fade(self)

func _cache_fade(node: Node) -> void:
	if node is MeshInstance3D:
		var original := node.material_override as BaseMaterial3D
		if original:
			var faded := original.duplicate() as BaseMaterial3D
			faded.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			_fade_meshes.append({"node":node,"original":original,"faded":faded})
	elif node is Label3D:
		_fade_labels.append({"node":node,"color":node.modulate,"outline":node.outline_modulate})
	elif node is Light3D:
		_fade_lights.append({"node":node,"energy":node.light_energy,"visible":node.visible})
	for child in node.get_children():
		_cache_fade(child)

func set_route_opacity(value: float) -> void:
	var amount := clampf(value,0.0,1.0)
	if amount == route_opacity:
		return
	route_opacity = amount
	visible = amount > 0.0
	for entry in _fade_meshes:
		if amount >= 1.0:
			entry.node.material_override = entry.original
		else:
			var color: Color = entry.original.albedo_color
			color.a *= amount
			entry.faded.albedo_color = color
			entry.node.material_override = entry.faded
	for entry in _fade_labels:
		var color: Color = entry.color
		var outline: Color = entry.outline
		color.a *= amount
		outline.a *= amount
		entry.node.modulate = color
		entry.node.outline_modulate = outline
	for entry in _fade_lights:
		entry.node.light_energy = entry.energy * amount
		entry.node.visible = entry.visible and amount > 0.0
