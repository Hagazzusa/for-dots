extends Node
## Read-only presentation of shared simulation time; never advances itself.
@export_range(90.0,600.0,1.0) var cycle_seconds := 180.0
@export_range(0.0,300.0,1.0) var lull_start := 45.0
@export_range(0.1,60.0,0.1) var fade_seconds := 12.0
@export_range(0.0,120.0,1.0) var hold_seconds := 18.0
var phase := 0.0
var strength := 0.0

func present(elapsed: float) -> void:
	if not is_finite(elapsed): return
	phase = fposmod(maxf(elapsed,0.0),maxf(cycle_seconds,1.0))
	var fade := maxf(fade_seconds,.001)
	var end_hold := lull_start + fade + hold_seconds
	strength = smoothstep(lull_start,lull_start+fade,phase) * (1.0-smoothstep(end_hold,end_hold+fade,phase))

func reset() -> void:
	present(0.0)
