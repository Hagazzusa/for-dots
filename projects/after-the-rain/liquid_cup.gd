extends Node3D
## Bounded, damped liquid approximation in an actually hollow tapered cup.
## No CFD or spill simulation: surface is constrained to the inner vessel.
var current_fill := 1.0
var target_fill := 1.0
var surface_height := .035
var max_surface_height := .035
var min_surface_height := .035
var slope := Vector2.ZERO
var velocity := Vector2.ZERO
var clock_time := 0.0
var liquid: MeshInstance3D
var liquid_material: StandardMaterial3D
const SEGMENTS := 48
const RINGS := 4
const INNER_BOTTOM := -.082
const INNER_TOP := .09
const RADIUS_BOTTOM := .053
const RADIUS_TOP := .067
const K := (RADIUS_TOP-RADIUS_BOTTOM)/(INNER_TOP-INNER_BOTTOM)

@export_range(0.0,1.0) var initial_fill := 1.0
@export_range(0.1,2.0) var fill_change_speed := .55
@export_range(1.0,60.0) var spring_strength := 30.0
@export_range(0.1,15.0) var spring_damping := 5.2

func radius_at(y: float) -> float:
	return RADIUS_BOTTOM + (y-INNER_BOTTOM)*K

func add_vertex(st: SurfaceTool, p: Vector3, n: Vector3):
	st.set_normal(n)
	st.add_vertex(p)

func _ready():
	# Stable hollow-vessel geometry is authored in cocoa_cup.tscn.
	# Only this per-instance liquid mesh is regenerated during play.
	liquid = $Liquid
	liquid_material = liquid.material_override.duplicate() as StandardMaterial3D
	liquid.material_override = liquid_material
	set_fill(initial_fill,true)
	update_liquid(0,Vector3.UP)

func set_fill(amount: float, immediate := false):
	target_fill = clampf(amount,0,1)
	if immediate:
		current_fill = target_fill
		slope = Vector2.ZERO
		velocity = Vector2.ZERO
	if liquid:
		liquid.visible = current_fill > .004

func impulse(force: Vector2):
	velocity += force.limit_length(1.2)
	velocity = velocity.limit_length(2.5)

func fill_height(fill: float) -> float:
	if fill <= 1.0/3:
		return lerpf(-.079,-.040,fill*3)
	if fill <= 2.0/3:
		return lerpf(-.040,-.002,(fill-1.0/3)*3)
	return lerpf(-.002,.035,(fill-2.0/3)*3)

func update_liquid(delta: float, world_up_local: Vector3):
	if not liquid:
		return
	var dt := clampf(delta,0,.05)
	clock_time += dt
	current_fill = move_toward(current_fill,target_fill,dt*fill_change_speed)
	# Semi-implicit spring; small substeps remain stable after long game frames.
	for substep in range(3):
		var step := dt/3
		velocity += (-spring_strength*slope-spring_damping*velocity)*step
		slope += velocity*step
		slope = slope.limit_length(.28)
	var denominator := maxf(absf(world_up_local.y),.22)
	var gravity_slope := Vector2(-world_up_local.x,-world_up_local.z)/denominator
	var total_slope := (gravity_slope+slope).limit_length(.8)
	var amp := minf(.0018,slope.length()*.008+velocity.length()*.0005)
	var desired := fill_height(current_fill)
	var excursion := .068*total_slope.length()+amp+.001
	# Headroom and base clearance always win over approximate volume conservation.
	surface_height = clampf(desired,-.079+excursion,.075-excursion)
	liquid.visible = current_fill > .004
	max_surface_height = -INF
	min_surface_height = INF
	if not liquid.visible:
		surface_height = -.079
		max_surface_height = -.079
		min_surface_height = -.079
		return
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for ring_index in range(RINGS):
		var f0 := float(ring_index)/RINGS
		var f1 := float(ring_index+1)/RINGS
		for i in range(SEGMENTS):
			var a := TAU*i/SEGMENTS
			var b := TAU*(i+1)/SEGMENTS
			var points := [surface_point(a,f0,total_slope,amp),surface_point(a,f1,total_slope,amp),surface_point(b,f1,total_slope,amp),surface_point(b,f0,total_slope,amp)]
			for index in [0,1,2,0,2,3]:
				var p: Vector3 = points[index]
				max_surface_height = maxf(max_surface_height,p.y)
				min_surface_height = minf(min_surface_height,p.y)
				var wave_gradient := cos(clock_time*6+p.x*65+p.z*32)*amp
				add_vertex(st,p,Vector3(-total_slope.x-wave_gradient*65,1,-total_slope.y-wave_gradient*32).normalized())
	liquid.mesh = st.commit()

func surface_point(angle: float, fraction: float, tilt: Vector2, amplitude: float) -> Vector3:
	var direction := Vector2(cos(angle),sin(angle))
	var gradient := tilt.dot(direction)
	# Solve r = radius_at(height + gradient*r) for exact tapered-wall contact.
	var edge_radius := (radius_at(surface_height)-.00018)/(1.0-K*gradient)
	var r := edge_radius*fraction
	var y := surface_height+gradient*r
	var wave := sin(clock_time*6+r*cos(angle)*65+r*sin(angle)*32)*amplitude
	wave *= (1-fraction)*.8
	# Restrained meniscus at wall, never a raised cap or dome.
	y += wave + pow(fraction,12)*.00035
	y = clampf(y,-.079,.075)
	r = minf(r,radius_at(y)-.00008)
	return Vector3(direction.x*r,y,direction.y*r)
