extends Resource
## Shared immutable tuning. Each NightBus owns its own route phase and elapsed time.
@export_range(0.1, 300.0, 0.1) var wait_seconds := 25.0
@export_range(0.1, 60.0, 0.1) var approach_seconds := 8.0
@export_range(0.1, 120.0, 0.1) var stop_seconds := 20.0
@export_range(0.1, 60.0, 0.1) var departure_seconds := 8.0
@export var approach_x := -34.0
@export var stop_x := 0.0
@export var departure_x := 36.0
@export var lane_z := 4.3
