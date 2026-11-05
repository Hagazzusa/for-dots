extends Node3D
## Composition root. No autoload; no project or source-file mutation.
@onready var refuge = $Refuge
@onready var pendant = $Pendant
@onready var rig = $ViewRig
@onready var status: Label = $UI/Panel/Margin/Rows/Status
@onready var lamp_button: Button = $UI/Panel/Margin/Rows/Buttons/Lamp
@onready var glass_button: Button = $UI/Panel/Margin/Rows/Buttons/Glass

func _ready() -> void:
	pendant.bind_globe(refuge.globe)
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

func toggle_lamp() -> void:
	pendant.set_on(not pendant.is_on)

func toggle_glass() -> void:
	refuge.set_glass_visible(not refuge.glass_visible)

func reset_all() -> void:
	rig.reset_view()
	pendant.set_on(true)
	refuge.set_glass_visible(true)

func update_status() -> void:
	status.text = "Lamp %s  •  Glass %s  •  Orbit-only architectural study" % ["ON" if pendant.is_on else "OFF", "ON" if refuge.glass_visible else "HIDDEN"]
	lamp_button.text = "L  Lamp: " + ("ON" if pendant.is_on else "OFF")
	glass_button.text = "G  Glass: " + ("ON" if refuge.glass_visible else "HIDDEN")
