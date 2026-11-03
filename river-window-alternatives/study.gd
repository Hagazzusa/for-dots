extends Node3D
## Independent spatial sketch, not the game's clock or route simulation.
var elapsed := 0.0
var playing := false
@onready var rig: Node3D = $RideRig
@onready var label: Label = $UI/Label
func _process(delta: float) -> void:
	if playing: elapsed = minf(elapsed + maxf(delta,0.0),24.0)
	rig.position.x = elapsed / 24.0 * 40.0
	label.text = "SPATIAL STUDY | stylized water / not game integration\nSpace: play / pause    R: restart    1 / 2 / 3: review positions    Esc: close study\n%.1f / 24 s | %.1f m | %s" % [elapsed,rig.position.x,"PLAY" if playing else "PAUSED"]
func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo(): return
	match event.keycode:
		KEY_SPACE: playing = not playing
		KEY_R: elapsed=0.0; playing=false
		KEY_1: elapsed=0.0; playing=false
		KEY_2: elapsed=12.0; playing=false
		KEY_3: elapsed=24.0; playing=false
		KEY_4: elapsed=19.0; playing=false
		KEY_ESCAPE: get_tree().quit()
