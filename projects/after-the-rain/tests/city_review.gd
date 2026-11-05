extends Node3D
@export var before := false
func _ready():
 preload("res://tests/fixture_marker.gd").attach(self)
 var game=load("res://tests/fixtures/main_before.tscn" if before else "res://main.tscn").instantiate()
 add_child(game)
 game.player.set_photo_view(Vector3(-3,1.8,1.9),Vector3(1,4,23))
 game.bus.set_paused(true)
 game.set_note("City streetscape / before" if before else "City streetscape / after",60)
 Input.mouse_mode=Input.MOUSE_MODE_VISIBLE

 await get_tree().create_timer(10).timeout
 var metrics={"fps":Performance.get_monitor(Performance.TIME_FPS),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"objects":Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)}
 var f=FileAccess.open("res://art/city_render_metrics.json",FileAccess.WRITE)
 f.store_string(JSON.stringify(metrics,"  "))
