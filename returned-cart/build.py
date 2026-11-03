"""Original empty delivery cart outside the workshop; no external assets, animation or game changes."""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;random.seed(18);DRAFT='--draft' in sys.argv
(R/'renders').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32 if DRAFT else 128;s.cycles.use_denoising=False;s.cycles.seed=18;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=900 if DRAFT else 1200;s.render.resolution_y=700 if DRAFT else 933;s.render.resolution_percentage=100;s.render.use_stamp=False;s.view_settings.view_transform='AgX';s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.33,.48,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.12

def mat(name,color,rough=.65,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
wood=mat('Old warm workbench',(.25,.12,.047));n=wood.node_tree.nodes;l=wood.node_tree.links;tc=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(3,65,35);l.new(tc.outputs['Generated'],scale.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;l.new(scale.outputs[0],noise.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.11,.045,.017,1);ramp.color_ramp.elements[1].color=(.36,.20,.09,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
wall=mat('Warm worn plaster',(.42,.40,.34));floor=mat('Slate floor',(.18,.21,.22));steel=mat('Dark used iron',(.075,.09,.095),.47,.65);pale=mat('Fresh wood inside',(.56,.34,.16));cloth=mat('Folded sage cloth',(.25,.30,.24),.95);blue=mat('Blue-gray pencil',(.12,.23,.29));graphite=mat('Graphite',(.025,.025,.025));glass=mat('Opaque stylized night pane',(.065,.13,.22),.23)
def box(name,loc,dims,ma,bevel=.006):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel: m=o.modifiers.new('Soft worn edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,radius,depth,ma,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=rotation);o=bpy.context.object;o.name=name;o.data.materials.append(ma);o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def curve(name,coords,r,ma):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(coords)-1)
 for p,co in zip(sp.points,coords):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(ma);return o
rubber=mat('Old soft gray wheels',(.055,.065,.068),.9)
# Closed workshop side door and a shallow sheltered strip, not a new game room.
box('Paving foundation',(0,0,-.04),(3.5,3.0,.08),floor)
for j in range(7):
 for i in range(7):
  x=(i-3)*.40+(j%2)*.2;y=(j-3)*.31
  box('Individual paving slab',(x,y,-.004),(.389,.299,.025),floor,.007)
box('Workshop wall',(0,.79,1.1),(3,.15,2.2),wall)
for i in range(7):box('Closed door plank',(-.43+i*.13,.695,.96),(.125,.045,1.82),wood,.002)
for x in (-.52,.48):box('Door jamb',(x,.64,1.0),(.075,.10,2.0),wood)
box('Door lintel',(-.02,.64,1.98),(1.10,.12,.08),wood)
box('Sheltered step',(-.02,.57,.07),(1.15,.28,.14),wall,.008)
cyl('Plain door handle',(.31,.635,.96),.012,.09,steel,(math.pi/2,0,0))
# Four wheels and their axle hardware support an empty low slatted bed.
pre_cart=set(bpy.data.objects)
for y in (-.38,.38):
 cyl('Axle',(0,y,.15),.025,.81,steel,(0,math.pi/2,0))
 for x in (-.37,.37):
  cyl('Wheel',(x,y,.15),.1415,.055,rubber,(0,math.pi/2,0));cyl('Wheel hub',(x+(.03 if x>0 else -.03),y,.15),.045,.012,steel,(0,math.pi/2,0))
for x in (-.26,.26):
 box('Underframe',(x,0,.29),(.055,1.02,.075),steel,.008)
 for y in (-.38,.38):box('Axle hanger',(x,y,.215),(.05,.05,.14),steel,.004)
for i in range(5):box('Cart bed slat',(-.27+i*.135,0,.355),(.127,1.08,.055),wood,.008)
# Handrail is open and plainly visible: nothing is being delivered now.
for x in (-.27,.27):curve('Empty cart handle',[(x,-.50,.32),(x,-.82,.74),(x,-.89,.88)],.019,steel)
curve('Cross handle',[(-.27,-.89,.88),(.27,-.89,.88)],.022,wood)
# One open asymmetric canvas ribbon, with unequal loose ends.
controls=[(.20,-.32),(.16,-.28),(.12,-.22)]
for i in range(19):
 t=-1.0+5.0*i/18
 controls.append((-.025+.18*math.cos(t)*(1+.06*math.sin(2*t)),.08+.26*math.sin(t)))
controls.extend([(-.205,-.13),(-.245,-.09),(-.250,-.035)])
# Catmull-Rom interpolation softens the open path without closing its ends.
path=[]
for j in range(len(controls)-1):
 a=Vector(controls[max(0,j-1)]);b=Vector(controls[j]);c=Vector(controls[j+1]);d=Vector(controls[min(len(controls)-1,j+2)])
 for k in range(8):
  t=k/8;path.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
path.append(Vector(controls[-1]));vs=[];fs=[]
for i,p in enumerate(path):
 tangent=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized();normal=Vector((-tangent.y,tangent.x));half=.011*(1+.05*math.sin(i*.17))
 # The strip lies against the slats, with a restrained small lifted bend.
 z=.3845+.002*math.exp(-((i/len(path)-.78)/.06)**2)
 for side in (-1,1):q=p+normal*half*side;vs.append((q.x,q.y,z))
for i in range(len(path)-1):a=i*2;fs.append((a,a+1,a+3,a+2))
me=bpy.data.meshes.new('Open slack strap ribbon');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Open asymmetric canvas strap',me);bpy.context.collection.objects.link(o);o.data.materials.append(cloth);mod=o.modifiers.new('Woven strap thickness','SOLIDIFY');mod.thickness=.002
# Move the entire cart clear of the step; wheel bottoms meet paving at 8.5mm.
for ob in set(bpy.data.objects)-pre_cart: ob.location.y-=.22
# The doorstep remains clear; no new actor, dialogue or collectible.
box('Eave beam',(0,.32,2.04),(2.7,.12,.10),wood)
def area(name,loc,target,power,size,color):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm eave light',(.3,.45,1.8),(0,-.25,.2),36,.55,(1,.75,.46))
area('Blue night sky',(-1.5,-.8,2.8),(0,0,.3),35,2.2,(.38,.56,1))
area('Gentle front fill',(1.5,-2.2,1.5),(0,0,.3),14,2,(.58,.70,1))
bpy.ops.object.camera_add(location=(1.8,-2.8,1.9));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.13,.60))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.35;s.camera=cam
s.render.image_settings.file_format='PNG';s.render.filepath='//returned_cart_draft.png' if DRAFT else '//renders/returned_cart_final.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(R/('Returned_Cart_Draft.blend' if DRAFT else 'Returned_Cart.blend')))
bpy.ops.render.render(write_still=True)
