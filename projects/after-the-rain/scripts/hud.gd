extends CanvasLayer
## Presentation only. The composition root supplies all game decisions.
@onready var hint: Label = $Hint
@onready var feeling: Label = $Feeling
@onready var bus_status: Label = $BusStatus
@onready var ending: Control = $Ending

func present(hint_text: String, feeling_text: String, status_text: String, ending_visible: bool) -> void:
	hint.text = hint_text
	feeling.text = feeling_text
	bus_status.text = status_text
	ending.visible = ending_visible

func set_riding(riding:bool,overview:bool=false):
	if overview:
		$Guide.text="P / E 돌아가기   Space pause/help   R restart   M mute"
		return
	$Guide.text = "Space pause/help   R restart   M mute   ESC release" if riding else "WASD walk   MOUSE / ARROWS look   E interact / sit / board   F cocoa / sip   U umbrella   Q close   Space pause/help   R restart   M mute   ESC release"

func set_clock(value:String)->void:
	$Subtitle.text="A SMALL PLACE TO REST     /     "+value
