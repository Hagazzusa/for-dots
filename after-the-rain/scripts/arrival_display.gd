extends Node3D
## Presentation only: the session supplies schedule data explicitly.
@onready var destination: Label3D = $Destination
@onready var arrival: Label3D = $Arrival

func present(phase: String, seconds: int) -> void:
	match phase:
		"waiting":
			arrival.text = "ARRIVES IN  %02ds" % maxi(0, seconds)
		"approaching":
			arrival.text = "ARRIVING"
		"stopped":
			arrival.text = "DOORS OPEN"
		"departing":
			arrival.text = "NEXT BUS SOON"
		_:
			arrival.text = "NIGHT SERVICE"
