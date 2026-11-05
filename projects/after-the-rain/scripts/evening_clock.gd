extends Node
## Composition root supplies simulation time and actual skipped waiting seconds.
## No OS clock, automatic processing or last-bus deadline.
@export_range(0,1439,1) var start_minutes := 1420
var elapsed := 0.0

func advance(seconds: float) -> void:
	if is_finite(seconds) and seconds > 0.0:
		elapsed += seconds

func time_text() -> String:
	var minute := (start_minutes + int(floor(elapsed/60.0))) % 1440
	return "%02d:%02d" % [int(minute/60.0), minute%60]

func reset() -> void:
	elapsed = 0.0
