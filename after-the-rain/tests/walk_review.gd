extends Node3D
var game
var index:=0
func _ready():
 preload("res://tests/fixture_marker.gd").attach(self)
 game=load("res://main.tscn").instantiate()
 add_child(game)
 game.bus.set_paused(true)
 show_target()
func show_target():
 var point:Vector3=game.exploration.basket.global_position if index==0 else game.exploration.flower.global_position
 game.player.set_photo_view(point+Vector3(0,.15,1.4),point)
 Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
func _unhandled_key_input(event):
 if event is InputEventKey and event.pressed and event.keycode==KEY_N:
  game.story.panel.close_story()
  index=1-index
  show_target()
 if event is InputEventKey and event.pressed and event.keycode==KEY_C:
  game.drink.request_action(true,false)
  game.drink.advance(1.5)
 if event is InputEventKey and event.pressed and event.keycode==KEY_B:
  game.restart()
  game.bus.advance(26)
  game.bus.advance(9)
  game.bus.set_paused(true)
  game.player.set_photo_view(Vector3(-5,2.1,2.25),Vector3(2,1.2,1.8))
  Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
