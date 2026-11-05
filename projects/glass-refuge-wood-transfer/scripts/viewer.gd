extends Node3D
## Composition root. No autoload; no project or source-file mutation.
var wood_resolution := 1024
var study_wood_material: StandardMaterial3D
@onready var refuge = $Refuge
@onready var pendant = $Pendant
@onready var rig = $ViewRig
@onready var status: Label = $UI/Panel/Margin/Rows/Status
@onready var lamp_button: Button = $UI/Panel/Margin/Rows/Buttons/Lamp
@onready var glass_button: Button = $UI/Panel/Margin/Rows/Buttons/Glass

func _ready() -> void:
	pendant.bind_globe(refuge.globe)
	var oak := refuge.get_node("Imported").find_child("Opaque_Oak", true, false) as MeshInstance3D
	study_wood_material = oak.mesh.surface_get_material(0).duplicate() as StandardMaterial3D
	study_wood_material.resource_local_to_scene = true
	study_wood_material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	study_wood_material.texture_repeat = false
	oak.material_override = study_wood_material
	set_wood_resolution(1024)
	$UI/Panel/Margin/Rows/Buttons/Wood.pressed.connect(toggle_wood)
	lamp_button.pressed.connect(toggle_lamp)
	glass_button.pressed.connect(toggle_glass)
	$UI/Panel/Margin/Rows/Buttons/Reset.pressed.connect(reset_all)
	pendant.changed.connect(func(_value: bool): update_status())
	refuge.glass_changed.connect(func(_value: bool): update_status())
	update_status()

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	var code: Key = event.physical_keycode if event.physical_keycode != 0 else event.keycode
	match code:
		KEY_B:
			toggle_wood()
		KEY_L:
			toggle_lamp()
		KEY_G:
			toggle_glass()
		KEY_R:
			reset_all()
		KEY_ESCAPE:
			rig.dragging = false
		_:
			return
	get_viewport().set_input_as_handled()

func set_wood_resolution(value: int) -> void:
	wood_resolution = value
	if study_wood_material:
		study_wood_material.albedo_texture = load("res://assets/wood_albedo_%d.png" % value)
	update_status()

func toggle_wood() -> void:
	set_wood_resolution(512 if wood_resolution == 1024 else 1024)

func toggle_lamp() -> void:
	pendant.set_on(not pendant.is_on)

func toggle_glass() -> void:
	refuge.set_glass_visible(not refuge.glass_visible)

func reset_all() -> void:
	rig.reset_view()
	set_wood_resolution(1024)
	pendant.set_on(true)
	refuge.set_glass_visible(true)

func update_status() -> void:
	status.text = "STUDY / Wood %d  •  Lamp %s  •  Glass %s  •  B switches atlas only" % [wood_resolution, "ON" if pendant.is_on else "OFF", "ON" if refuge.glass_visible else "HIDDEN"]
	$UI/Panel/Margin/Rows/Buttons/Wood.text = "B  Wood: %d" % wood_resolution
	lamp_button.text = "L  Lamp: " + ("ON" if pendant.is_on else "OFF")
	glass_button.text = "G  Glass: " + ("ON" if refuge.glass_visible else "HIDDEN")
