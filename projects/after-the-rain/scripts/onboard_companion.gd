extends Node3D
## Saved peripheral evidence of the actual same-bus passenger. No inferred presence.
var companion_present := false
var has_loan := false
@onready var umbrella: Node3D = $FoldedUmbrella
func _ready() -> void: reset()
func configure(present: bool, loan: bool) -> void:
	companion_present = present
	has_loan = present and loan
	visible = companion_present
	umbrella.visible = has_loan
func reset() -> void:
	configure(false,false)
