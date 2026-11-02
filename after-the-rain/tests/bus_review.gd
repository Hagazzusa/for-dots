extends Node3D
## Isolated visual QA entry point; production main scene is unchanged.
func _ready():
 preload("res://tests/fixture_marker.gd").attach(self)
 var game=load("res://main.tscn").instantiate()
 add_child(game)
 game.bus.advance(26)
 game.bus.advance(9)
 game.bus.set_paused(true)
 game.player.set_photo_view(Vector3(7,2.5,.1),Vector3(1.4,1.3,4.3))
 game.set_note("Boarding geometry review / curb side",60)
 Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
