extends Node3D
## Original procedural night bus. Facing +X; passenger door on the -Z side.
var doors: Array[Node3D] = []
var door_tween: Tween
var door_open := false

func mat(color: Color, glow := 0.0, rough := .55) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	if glow > 0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = glow
	return m

func block(pos: Vector3, size: Vector3, surface: Material, parent: Node3D = self) -> MeshInstance3D:
	var n := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	n.mesh = mesh
	n.material_override = surface
	parent.add_child(n)
	n.position = pos
	return n

func _ready():
	var teal := mat(Color("1b5960"),0,.35)
	var cream := mat(Color("d6c8a2"))
	var black := mat(Color("101e27"))
	var warm := mat(Color("e1ba70"),.75)
	var glass := mat(Color("617d76"),.16,.25)
	var steel := mat(Color("849c99"),0,.3)
	# Continuous underfloor and roof; separate side sections leave a real door opening.
	block(Vector3(0,.58,0),Vector3(7.5,.35,2.3),teal)
	block(Vector3(0,.94,.99),Vector3(7.4,.45,.25),teal)
	block(Vector3(-.95,.94,-.99),Vector3(5.4,.45,.25),teal)
	block(Vector3(3.42,1.5,-.99),Vector3(.55,1.7,.25),teal)
	block(Vector3(0,2.62,0),Vector3(7.65,.2,2.36),cream)
	block(Vector3(0,2.77,0),Vector3(5.9,.14,1.7),teal)
	block(Vector3(0,1.18,1.12),Vector3(7.4,.13,.08),cream)
	block(Vector3(-.95,1.18,-1.12),Vector3(5.4,.13,.08),cream)
	block(Vector3(0,.42,0),Vector3(6.8,.12,1.8),black)
	# Warm opaque window panes and cream mullions.
	for z in [-1.08,1.08]:
		for i in range(6):
			var x := -3.1+float(i)*1.12
			if z<0 and x>1.6:
				continue
			block(Vector3(x,1.91,z),Vector3(.96,1.16,.07),glass)
			block(Vector3(x,2.44,z),Vector3(.9,.035,.085),warm)
			block(Vector3(x-.53,1.91,z),Vector3(.08,1.35,.13),cream)
			block(Vector3(x,1.38,z),Vector3(.96,.05,.09),steel)
	# Front (+X) and rear end, with a wide windscreen.
	block(Vector3(3.68,1.02,0),Vector3(.18,.6,2.25),cream)
	block(Vector3(3.69,1.93,0),Vector3(.1,1.15,2.15),glass)
	block(Vector3(3.76,1.93,0),Vector3(.035,1.15,.055),black)
	block(Vector3(3.69,2.5,0),Vector3(.15,.16,2.3),teal)
	block(Vector3(-3.67,1.55,0),Vector3(.15,1.95,2.25),teal)
	block(Vector3(-3.76,2.05,0),Vector3(.03,.75,1.85),glass)
	block(Vector3(3.8,.64,0),Vector3(.18,.14,2.4),steel)
	block(Vector3(-3.8,.64,0),Vector3(.18,.14,2.4),steel)
	for z in [-.78,.78]:
		block(Vector3(3.79,.98,z),Vector3(.04,.24,.44),mat(Color("fff2c4"),3))
		block(Vector3(-3.78,1.08,z),Vector3(.04,.29,.2),mat(Color("eb6742"),1.4))
		var beam := OmniLight3D.new()
		beam.light_color = Color("ffe8bb")
		beam.light_energy = 1.3
		beam.omni_range = 6
		add_child(beam)
		beam.position = Vector3(4.1,.9,z)
	# Wheels: cylinder's Y axis rotated onto Z.
	for x in [-2.35,2.35]:
		for z in [-1.18,1.18]:
			var wheel := MeshInstance3D.new()
			var cylinder := CylinderMesh.new()
			cylinder.top_radius = .48
			cylinder.bottom_radius = .48
			cylinder.height = .22
			cylinder.radial_segments = 20
			wheel.mesh = cylinder
			wheel.material_override = black
			add_child(wheel)
			wheel.rotation.x = PI/2
			wheel.position = Vector3(x,.45,z)
			var hub := MeshInstance3D.new()
			var disc := CylinderMesh.new()
			disc.top_radius = .25
			disc.bottom_radius = .25
			disc.height = .235
			disc.radial_segments = 12
			hub.mesh = disc
			hub.material_override = steel
			wheel.add_child(hub)
	# Door jamb and lighted steps. Gap is 1.3m wide.
	block(Vector3(2.4,.7,-.8),Vector3(1.3,.15,.7),warm)
	block(Vector3(2.4,.5,-1.0),Vector3(1.3,.12,.45),black)
	block(Vector3(2.4,2.49,-1.13),Vector3(1.4,.1,.12),cream)
	block(Vector3(2.4,1.62,-.45),Vector3(1.25,1.8,.06),warm)
	for i in range(2):
		var panel := Node3D.new()
		add_child(panel)
		panel.position = Vector3(2.075+i*.65,1.57,-1.18)
		doors.append(panel)
		block(Vector3.ZERO,Vector3(.62,1.8,.08),teal,panel)
		block(Vector3(0,.2,-.05),Vector3(.49,1.16,.02),glass,panel)
		block(Vector3(.2,0,-.07),Vector3(.025,.32,.035),cream,panel)
	var entrance_light := OmniLight3D.new()
	entrance_light.light_color = Color("ffd694")
	entrance_light.light_energy = 1.3
	entrance_light.omni_range = 3.8
	add_child(entrance_light)
	entrance_light.position = Vector3(2.4,2.2,-1.25)
	block(Vector3(-.25,2.38,-1.15),Vector3(2.5,.3,.08),black)
	var sign := Label3D.new()
	sign.text = "08 / HOME"
	sign.font_size = 42
	sign.pixel_size = .0045
	sign.modulate = Color("ffdaa0")
	sign.outline_size = 0
	sign.position = Vector3(-.25,2.38,-1.21)
	sign.rotation.y = PI
	add_child(sign)

func set_door_open(value: bool):
	door_open = value
	if door_tween:
		door_tween.kill()
	door_tween = create_tween().set_parallel(true)
	for i in range(doors.size()):
		var target_x := 2.075+i*.65
		if value:
			target_x += -.55 if i==0 else .55
		door_tween.tween_property(doors[i],"position:x",target_x,.7).set_trans(Tween.TRANS_SINE)
