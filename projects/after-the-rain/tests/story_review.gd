extends Node3D
var game
var index := 0
var ids := ["Memo","Route","Radio"]
func _ready():
 preload("res://tests/fixture_marker.gd").attach(self)
 game=load("res://main.tscn").instantiate()
 add_child(game)
 game.bus.set_paused(true)
 show_target()
func show_target():
 var point:Vector3=game.story.objects.get_node(ids[index]+"/Interaction").global_position
 game.player.set_photo_view(point+Vector3(0,.15,1.4),point)
 Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
func _unhandled_key_input(event):
 if event is InputEventKey and event.pressed and event.keycode==KEY_N:
  game.story.panel.close_story()
  index=(index+1)%ids.size()
  show_target()
