"""Build an original, static, editor-visible parked-car vignette using Godot primitives.
Original primitive geometry, visually guided by the generated blue-grey hatchback concept.
No external runtime assets or engine execution. Front is local -Z; measurements are artistic.
This is a stylized interpretation, not a photoreal or exact vehicle reconstruction.
Run with Python 3 to regenerate ../scenes/parked_car.tscn. Does not change other files.
"""
from pathlib import Path
from math import pi

OUT = Path(__file__).resolve().parents[1] / 'scenes' / 'parked_car.tscn'
resources=[]
nodes=[]

def vec(values):
    return 'Vector3(%s)' % ', '.join(f'{v:.6g}' for v in values)

def material(name, color, rough=.7, metal=0, alpha=1, emission=None):
    s=f'[sub_resource type="StandardMaterial3D" id="{name}"]\nalbedo_color = Color({", ".join(map(str,color))}, {alpha})\nroughness = {rough}\nmetallic = {metal}\n'
    if alpha < 1:
        s+='transparency = 1\ncull_mode = 2\n'
    if emission:
        s+=f'emission_enabled = true\nemission = Color({", ".join(map(str,emission))}, 1)\nemission_energy_multiplier = 0.6\n'
    resources.append(s)

material('Body',(.15,.22,.29),.27,.5)
material('Chrome',(.44,.49,.46),.3,.75)
material('Rubber',(.023,.029,.028),.95)
material('Interior',(.055,.067,.062),.9)
material('Seat',(.14,.18,.17),.9)
material('Glass',(.36,.53,.53),.26,0,.075)
material('Headlamp',(.75,.74,.55),.32)
material('TailLamp',(.38,.055,.038),.4)
# Restrained stylized ambient fill keeps both faces readable through rainy glazing.
material('SkinA',(.57,.38,.26),.92,emission=(.114,.076,.052))
material('SkinB',(.63,.44,.31),.92,emission=(.126,.088,.062))
material('Hair',(.055,.045,.035),.95)
material('CoatA',(.16,.20,.14),.93)
material('CoatB',(.16,.145,.125),.93)
material('Scarf',(.36,.15,.10),.95)
material('Trousers',(.07,.09,.1),.95)
material('Cardboard',(.39,.28,.16),.95)
material('Tape',(.55,.44,.27),.86)
material('Card',(.72,.66,.48),.95)
material('Lamp',(.97,.7,.34),.5,emission=(1,.56,.19))

def node(name,typ='Node3D',parent='.',pos=(0,0,0),rot=None,props=''):
    s=f'[node name="{name}" type="{typ}" parent="{parent}"]\nposition = {vec(pos)}\n'
    if rot:s+=f'rotation = {vec(rot)}\n'
    nodes.append(s+props)

def shape(name,kind,settings,mat,pos,rot=None,parent='.'):
    mesh='Mesh'+str(len(resources))
    resources.append(f'[sub_resource type="{kind}" id="{mesh}"]\n'+settings+'\n')
    node(name,'MeshInstance3D',parent,pos,rot,f'mesh = SubResource("{mesh}")\nmaterial_override = SubResource("{mat}")\n')

def box(name,size,mat,pos,rot=None,parent='.'):
    shape(name,'BoxMesh','size = '+vec(size),mat,pos,rot,parent)

def sphere(name,r,h,mat,pos,parent='.'):
    shape(name,'SphereMesh',f'radius = {r}\nheight = {h}\nradial_segments = 12\nrings = 6',mat,pos,parent=parent)

def cylinder(name,r,h,mat,pos,rot=None,parent='.'):
    shape(name,'CylinderMesh',f'top_radius = {r}\nbottom_radius = {r}\nheight = {h}\nradial_segments = 12\nrings = 1',mat,pos,rot,parent)

# A hollow passenger compartment, rather than occupants embedded inside a solid body.
box('LowerChassis',(1.72,.30,4.05),'Body',(0,.48,0))
box('CabinFloor',(1.55,.10,2.35),'Interior',(0,.67,.03))
box('Hood',(1.72,.24,1.10),'Body',(0,.83,-1.45))
box('HatchLowerPanel',(1.72,.27,.35),'Body',(0,.87,1.80))
box('Roof',(1.66,.105,2.30),'Body',(0,1.66,.25))
box('FrontBumper',(1.83,.13,.13),'Chrome',(0,.49,-2.07))
box('RearBumper',(1.83,.13,.13),'Chrome',(0,.49,2.07))
box('Grille',(1.02,.18,.03),'Rubber',(0,.71,-2.032))
for x,side in [(-.895,'Left'),(.895,'Right')]:
    for z,axle in [(-1.31,'Front'),(1.29,'Rear')]:
        cylinder(side+axle+'Tyre',.34,.20,'Rubber',(x,.35,z),(0,0,pi/2))
        cylinder(side+axle+'Hub',.20,.212,'Chrome',(x,.35,z),(0,0,pi/2))
    box(side+'Sill',(.075,.12,2.55),'Chrome',(x,.55,.02))
    for z,door,length in [(-.43,'Front',1.28),(.93,'Rear',1.35)]:
        box(side+door+'Door',(.055,.34,length),'Body',(x,.86,z))
        box(side+door+'Window',(.012,.51,length-.15),'Glass',(x,1.31,z))
        box(side+door+'Handle',(.065,.025,.16),'Chrome',(x*1.025,1.00,z+.35))
    # Pillars are narrow enough to preserve the side-window view of both seated adults.
    box(side+'MiddlePillar',(.065,.68,.075),'Body',(x,1.29,.24))
    box(side+'FrontPillar',(.07,.72,.07),'Body',(x,1.28,-1.045),(.34,0,0))
    box(side+'RearPillar',(.07,.72,.07),'Body',(x,1.28,1.60),(-.48,0,0))
    box(side+'Mirror',(.19,.105,.22),'Body',(x*1.13,1.11,-.9))
    box(side+'Headlight',(.35,.18,.025),'Headlamp',(x*.74,.83,-2.01))
    box(side+'Taillight',(.29,.16,.025),'TailLamp',(x*.76,.88,1.965))
box('Windshield',(1.65,.66,.012),'Glass',(0,1.29,-1.025),(.34,0,0))
box('RearWindow',(1.65,.69,.012),'Glass',(0,1.30,1.60),(-.48,0,0))
box('Dashboard',(1.55,.13,.25),'Interior',(0,.98,-.89))
box('RearBench',(1.46,.15,.48),'Seat',(0,.78,.79))
box('RearBenchBack',(1.46,.40,.12),'Seat',(0,1.00,1.05),(.10,0,0))
for x,label,coat,skin in [(-.43,'Driver','CoatA','SkinA'),(.43,'Passenger','CoatB','SkinB')]:
    box(label+'SeatBase',(.55,.13,.58),'Seat',(x,.76,-.28))
    box(label+'SeatBack',(.54,.50,.14),'Seat',(x,1.02,.01),(.10,0,0))
    box(label+'Headrest',(.31,.18,.10),'Seat',(x,1.32,.02))
    node(label,pos=(x,0,-.24))
    box('Torso',(.35,.39,.23),coat,(0,1.02,0),parent=label)
    cylinder('Neck',.065,.08,skin,(0,1.255,-.005),parent=label)
    sphere('Head',.125,.31,skin,(0,1.41,-.012),label)
    sphere('Hair',.13,.17,'Hair',(0,1.505,.015),label)
    box('Nose',(.04,.05,.045),skin,(0,1.405,-.143),parent=label)
    for eye_x,eye_name in [(-.045,'LeftEye'),(.045,'RightEye')]:
        sphere(eye_name,.012,.016,'Hair',(eye_x,1.442,-.122),label)
    if label=='Driver':
        sphere('HairBun',.065,.13,'Hair',(0,1.47,.118),label)
        box('RustScarf',(.28,.11,.255),'Scarf',(0,1.20,-.012),parent=label)
    for dx,part in [(-.12,'Left'),(.12,'Right')]:
        box(part+'Thigh',(.15,.14,.40),'Trousers',(dx,.815,-.18),parent=label)
        box(part+'LowerLeg',(.13,.26,.14),'Trousers',(dx,.68,-.38),parent=label)
        box(part+'Sleeve',(.105,.28,.13),coat,(dx*1.6,1.015,-.025),(.18,0,dx*.3),label)
        sphere(part+'Hand',.052,.10,skin,(dx*1.6,.89,-.08),label)
# A folded moving box remains behind the two front occupants; the move is finished.
box('LastMovingBox',(.64,.10,.50),'Cardboard',(.24,.905,.73))
box('BoxTape',(.08,.006,.51),'Tape',(.24,.958,.73))
box('BoxTapeFront',(.08,.10,.007),'Tape',(.24,.905,.475))
# The full handwritten card wording belongs to the game's accessible reader.
box('DashboardCard',(.22,.008,.13),'Card',(.43,1.05,-.86))
box('CardFirstLine',(.15,.003,.005),'Hair',(.43,1.056,-.88))
box('CardSecondLine',(.10,.003,.005),'Hair',(.405,1.056,-.84))
shape('SteeringWheel','TorusMesh','inner_radius = 0.125\nouter_radius = 0.165\nrings = 12\nring_segments = 6','Rubber',(-.43,1.04,-.71),(1.0,0,0))
box('CabinLight',(.12,.025,.12),'Lamp',(0,1.596,-.32))
node('InteriorWarmth','OmniLight3D',pos=(0,1.44,-.35),props='light_color = Color(1, 0.67, 0.35, 1)\nlight_energy = 0.55\nomni_range = 2.2\nshadow_enabled = false\n')
resources.append('[sub_resource type="BoxShape3D" id="Collision"]\nsize = Vector3(1.86, 1.64, 4.2)\n')
node('ChassisCollision','StaticBody3D',props='collision_layer = 1\ncollision_mask = 1\n')
node('Shape','CollisionShape3D','ChassisCollision',(0,.83,0),props='shape = SubResource("Collision")\n')
header=f'[gd_scene load_steps={len(resources)+1} format=3]\n\n'
root='[node name="ParkedCar" type="Node3D"]\nmetadata/front_direction = "-Z"\nmetadata/occupants = "Two seated adults; a stationary fictional vignette"\n\n'
OUT.write_text(header+'\n'.join(resources)+'\n'+root+'\n'.join(nodes))
print(f'Wrote {OUT.name}: {len(nodes)+1} saved nodes, {len(resources)} subresources')
assert len(nodes)+1<=100
