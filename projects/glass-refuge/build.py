"""Original procedural reconstruction of a single GPT Image concept.
Blender 4.3+, no third-party assets. See README for inferred dimensions/limits.
Run: blender -b -t 2 --python build.py -- --preview
"""
import bpy, math, random, os, sys, json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent
random.seed(31)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.collections):
    if d.name!='Collection': bpy.data.collections.remove(d)
base=bpy.data.collections.get('Collection'); base.name='00 | Reference & guides'
def collection(name):
 c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c
C={k:collection(n) for k,n in [('frame','01 | Laminated timber structure'),('metal','02 | Copper caps & fixings'),('glass','03 | Glazing panels'),('panels','04 | Sage boarding & sills'),('bench','05 | Bench & textiles'),('plants','06 | Refuge planting'),('stone','07 | Stone terrace & wet path'),('land','08 | Landscape study'),('light','09 | Lighting'),('camera','10 | Cameras')]}
def put(o,key):
 for c in list(o.users_collection): c.objects.unlink(o)
 C[key].objects.link(o); return o

def material(name,color,rough=.4,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
wood=material('Oak | long grain / warm honey',(.28,.13,.045),.35)
n=wood.node_tree.nodes;l=wood.node_tree.links;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=3.5;t.inputs['Detail'].default_value=3
tex=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(5,5,.23);l.new(tex.outputs['Generated'],v.inputs[0]);l.new(v.outputs['Vector'],t.inputs['Vector'])
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.2;r.color_ramp.elements[0].color=(.075,.028,.009,1);r.color_ramp.elements[1].position=.8;r.color_ramp.elements[1].color=(.31,.155,.055,1);l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.17;b.inputs['Distance'].default_value=.018;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
copper=material('Copper | rain-darkened brushed caps',(.30,.105,.055),.31,.8)
n=copper.node_tree.nodes;l=copper.node_tree.links;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=12;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.055,.025,.018,1);r.color_ramp.elements[1].color=(.48,.21,.115,1);l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
sage=material('Sage | painted tongue-and-groove',(.105,.145,.12),.56)
dark=material('Bronze | fittings',(.06,.042,.023),.29,.75)
glass=material('Glass | rain-softened low-iron 6mm',(.85,.94,.98),.015)
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
n=glass.node_tree.nodes;l=glass.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=125;t.inputs['Detail'].default_value=2;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.035;b.inputs['Distance'].default_value=.0006;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
stone=material('Basalt | wet weathered stone',(.10,.12,.135),.24)
n=stone.node_tree.nodes;l=stone.node_tree.links;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=5;t.inputs['Detail'].default_value=4;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.025,.035,.045,1);r.color_ramp.elements[1].color=(.22,.23,.22,1);l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.55;b.inputs['Distance'].default_value=.055;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
soil=material('Damp earth',(.028,.035,.025),.9)
leafm=[material('Foliage | '+n,c,.7) for n,c in [('sage',(.16,.21,.10)),('olive',(.24,.28,.09)),('deep',(.055,.10,.045)),('gold',(.38,.29,.11))]]
fabric=material('Linen | natural flax',(.45,.36,.23),.95);olive=material('Linen | olive cushion',(.26,.27,.095),.9)
for m in [fabric,olive]:
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=220;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.008;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])

def cube(name,loc,dim,mat,key,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);put(o,key)
 if bevel: mod=o.modifiers.new('Soft worked edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def mesh(name,verts,faces,mat,key):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);C[key].objects.link(o);o.data.materials.append(mat);return o

def cylinder(name,a,b,r,mat,key,verts=12):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);put(o,key);return o

def sphere(name,loc,scale,mat,key,seg=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=12,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);put(o,key)
 for p in o.data.polygons:p.use_smooth=True
 return o
F=.42;R=1.6;S=2.48;Y0=-1.6;Y1=1.6
# Arch segments are closed radial solids; all geometry remains separately editable.
def arch(name,y,r0,r1,depth,mat,key,start=0,end=math.pi,n=64):
 vs=[]
 for j in range(n+1):
  t=start+(end-start)*j/n
  for yy,rr in [(y-depth/2,r0),(y+depth/2,r0),(y+depth/2,r1),(y-depth/2,r1)]:vs.append((rr*math.cos(t),yy,S+rr*math.sin(t)))
 fs=[(0,3,2,1)]
 for j in range(n):
  a=j*4;b=(j+1)*4
  for k in range(4):fs.append((a+k,a+(k+1)%4,b+(k+1)%4,b+k))
 fs.append(tuple(n*4+k for k in range(4)))
 o=mesh(name,vs,[tuple(reversed(f)) for f in fs],mat,key);be=o.modifiers.new('Rounded lamination edges','BEVEL');be.width=.008;be.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
ys=[-1.6,-.8,0,.8,1.6]
for i,y in enumerate(ys):
 arch(f'Rib {i+1:02} | curved oak',y,R-.07,R+.07,.135,wood,'frame')
 arch(f'Rib {i+1:02} | copper weather cap',y,R+.074,R+.09,.175,copper,'metal')
 for side in [-1,1]:
  cube(f'Rib {i+1:02} | post {side}',(side*R,y,(F+S)/2),(.14,.14,S-F),wood,'frame',.009)
  cube('Copper post shoe',(side*R,y,F+.13),(.155,.155,.26),copper,'metal',.008)
  for z in [F+.07,F+.20]:
   sphere('Bronze shoe pin',(side*R,y-.082,z),(.018,.009,.018),dark,'metal',12)
# Roof glazing segmented over bays, slightly above timber. Closed 6mm-shell solids.
for i in range(4):
 for j in range(3):
  arch(f'Roof glazing | bay {i+1} segment {j+1}',(ys[i]+ys[i+1])/2,R+.025,R+.031,.655,glass,'glass',j*math.pi/3+.007,(j+1)*math.pi/3-.007,24)
# Long roof glazing bars
for t in [math.pi/3,2*math.pi/3]:
 cylinder('Bronze glazing seam',(R*math.cos(t),Y0,S+R*math.sin(t)),(R*math.cos(t),Y1,S+R*math.sin(t)),.022,dark,'metal')
# Vertical side elevations with individual boards, translucent glass and sills
for side in [-1,1]:
 x=side*R
 cube('Oak eave beam',(x,0,S),(.13,3.34,.12),wood,'frame',.008)
 cube('Sage lower sill',(x,0,F+.055),(.17,3.34,.11),sage,'panels',.008)
 cube('Oak / sage panel top rail',(x,0,F+.91),(.18,3.34,.10),sage,'panels',.009)
 for i in range(20):cube('Vertical sage board',(x,Y0+.08+i*.16,F+.47),(.075,.153,.79),sage,'panels',.004)
 for i in range(4):cube(f'Side window {side} / {i+1}',(x,(ys[i]+ys[i+1])/2,(F+.96+S)/2),(.006,.66,S-F-.96),glass,'glass')
# Rear elevation: lower boarding, broad glass, arched fanlight
for i in range(20):cube('Rear sage board',(-1.52+i*.16,Y1,F+.47),(.153,.075,.8),sage,'panels',.004)
cube('Rear sill',(0,Y1,F+.91),(3.2,.16,.1),sage,'panels',.008)
cube('Rear transom',(0,Y1,S),(3.2,.12,.1),wood,'frame',.008)
cube('Rear glass lower',(0,Y1,(F+.96+S)/2),(3.06,.006,S-F-.96),glass,'glass')
def fanlight(name,y,left=-R,right=R):
 # rear closed half-disc pane, flattened depth, front segment optional
 vs=[(left,y,S),(right,y,S)];steps=48
 for j in range(1,steps):
  x=right+(left-right)*j/steps;vs.append((x,y,S+math.sqrt(max(0,R*R-x*x))))
 o=mesh(name,vs,[tuple(range(len(vs)))],glass,'glass');m=o.modifiers.new('6 mm pane thickness','SOLIDIFY');m.thickness=.006
fanlight('Rear arched glazing',Y1)
# Asymmetric front sidelight, opening deliberately has no glass or door.
DX=-.65;cube('Front entrance jamb',(DX,Y0,(F+S+math.sqrt(R*R-DX*DX))/2),(.16,.18,S+math.sqrt(R*R-DX*DX)-F),wood,'frame',.012)
cube('Entrance jamb copper shoe',(DX,Y0,F+.12),(.18,.20,.24),copper,'metal',.006)
for i in range(5):cube('Front sidelight sage board',(-1.50+i*.17,Y0,F+.47),(.163,.075,.8),sage,'panels',.004)
cube('Front sidelight sill',((-R+DX)/2,Y0,F+.91),(R+DX,.16,.1),sage,'panels',.008)
cube('Front sidelight glass',((-R+DX)/2,Y0,(F+.96+S)/2),(R+DX-.1,.006,S-F-.96),glass,'glass')
# Irregular polygon shaped upper sidelight beneath arch
vs=[(-R+.07,Y0,S),(DX-.08,Y0,S),(DX-.08,Y0,S+math.sqrt(R*R-(DX-.08)**2)-.08)]
for j in range(1,33):
 x=DX-.08+(-R+.07-(DX-.08))*j/32;vs.append((x,Y0,S+math.sqrt(max(0,R*R-x*x))-.06))
o=mesh('Front upper sidelight',vs,[tuple(range(len(vs)))],glass,'glass');o.modifiers.new('6mm glass','SOLIDIFY').thickness=.006
cube('Front sidelight transom',((-R+DX)/2,Y0,S),(R+DX,.10,.075),wood,'frame',.006)
# Bolt details visible around front copper cap
for j in range(15):
 t=.04+(math.pi-.08)*j/14;x=(R+.025)*math.cos(t);z=S+(R+.025)*math.sin(t)
 sphere('Copper cap rivet',(x,Y0-.092,z),(.014,.008,.014),dark,'metal',12)
# Bench across rear, fitted clear of side walls
for x in [-1.22,0,1.22]:
 cube('Bench oak leg',(x,.94,F+.245),(.10,.10,.49),wood,'bench',.015)
 cube('Bench rear upright',(x,1.30,F+.59),(.08,.10,1.12),wood,'bench',.01)
for y in [.78,.96,1.14]:cube('Bench seat slat',(0,y,F+.51),(2.75,.17,.075),wood,'bench',.015)
for z in [.72,.91,1.10]:cube('Bench back slat',(0,1.28,F+z),(2.78,.075,.17),wood,'bench',.015)
def pillow(name,x,y,z,mat,tilt=0):
 o=cube(name,(x,y,z),(.57,.19,.55),mat,'bench',.10);o.rotation_euler=(math.radians(-12),tilt,math.radians(random.uniform(-7,7)));return o
pillow('Flax cushion',-1.01,1.10,F+.81,fabric,-.1);pillow('Olive cushion',.61,1.10,F+.81,olive,.15);pillow('Flax cushion',1.07,1.10,F+.81,fabric,-.12)
# Draped throw as a wave-shaped editable quad sheet, with fringe
vs=[];fs=[]
for j in range(31):
 t=j/30
 if t<.52:y=1.25-t*1.1;z=F+.56+.018*math.sin(t*12)
 else:y=.678-.018*math.sin((t-.52)*6);z=F+.56-(t-.52)*.83
 for i in range(13):vs.append((-.94+(i/12-.5)*.46,y,z+.018*math.cos(i*2.1)))
for j in range(30):
 for i in range(12):a=j*13+i;fs.append((a,a+1,a+14,a+13))
o=mesh('Woven throw | draped over seat',vs,fs,fabric,'bench');o.modifiers.new('Textile thickness','SOLIDIFY').thickness=.006
for i in range(20):
 x=-1.17+i*.024;cylinder('Throw fringe',(x,.675,F+.17),(x+random.uniform(-.01,.01),.675,F+.095+random.random()*.02),.003,fabric,'bench',5)
# Right-side raised planter, below sill
cube('Planter soil',(1.24,-.30,F+.86),(.42,1.60,.06),soil,'plants',.02)
for x in [1.00,1.49]:cube('Planter long wall',(x,-.30,F+.62),(.055,1.70,.52),sage,'plants',.008)
for y in [-1.15,.55]:cube('Planter end',(1.245,y,F+.62),(.54,.06,.52),sage,'plants',.01)
# Small procedural shrubs: tapered branching stems and leaf clusters, no asset downloads
for k in range(30):
 x=random.uniform(1.05,1.42);y=random.uniform(-1.08,.48);h=random.uniform(.42,1.07);a=Vector((x,y,F+.9));tip=a+Vector((random.uniform(-.12,.12),random.uniform(-.12,.12),h));cylinder('Planter stem',a,tip,.007,leafm[2],'plants',6)
 for j in range(5):
  p=a.lerp(tip,.22+j*.14);q=p+Vector((random.uniform(-.22,.22),random.uniform(-.22,.22),random.uniform(.10,.20)));cylinder('Fine twig',p,q,.003,leafm[2],'plants',5)
  for u in [.4,.7,1]:
   o=sphere('Herb leaf',p.lerp(q,u),(.026,.065,.013),random.choice(leafm),'plants',8);o.rotation_euler=(random.random(),random.random(),random.random()*6.28)
# Pendant
em=material('Opal globe | warm emission',(.95,.68,.31),.25);p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.57,.20,1);p.inputs['Emission Strength'].default_value=3
cylinder('Pendant braided cord',(0,-.55,3.95),(0,-.55,3.02),.012,dark,'light');cylinder('Pendant brass socket',(0,-.55,3.04),(0,-.55,2.95),.055,copper,'light',24);sphere('Pendant opal globe',(0,-.55,2.77),(.24,.24,.24),em,'light',40)
# Wet platform with fitted irregular stone blocks and front two steps
cube('Terrace foundation',(0,0,.17),(4.7,4.5,.34),stone,'stone',.08)
for row in range(7):
 for col in range(8):
  x=-2.04+col*.58+random.uniform(-.025,.025);y=-1.98+row*.65+random.uniform(-.02,.02)
  o=cube('Terrace paving stone',(x,y,.37+random.uniform(-.012,.012)),(.56+random.uniform(-.03,.02),.625,.10),stone,'stone',.035);o.rotation_euler.z=random.uniform(-.025,.025)
for i in range(9):
 cube('Rough terrace edge block',(-2.1+i*.52,-2.27,.16),(.50,.28,.32),stone,'stone',.045)
for z,y,w in [(.09,-2.70,2.4),(.20,-2.42,2.6)]:
 for i in range(4):cube('Entry step block',(-w/2+w/8+i*w/4,y,z),(w/4-.025,.44,.18),stone,'stone',.045)
# Approach flagstones
for row in range(6):
 for col in range(5):
  o=cube('Approach wet flagstone',(-1.6+col*.80+(row%2)*.2,-3.3-row*.60,-.012),(.77,.56,.08),stone,'stone',.04);o.rotation_euler.z=random.uniform(-.035,.035)
cube('Ground',(0,0,-.12),(200,24,.18),soil,'land')
# Lightly broken corners and uneven tops; deliberately not perfect tile grids.
for ob in C['stone'].objects:
 if 'paving stone' in ob.name or 'flagstone' in ob.name or 'edge block' in ob.name:
  for v in ob.data.vertices:
   v.co.x+=random.uniform(-.035,.035);v.co.y+=random.uniform(-.025,.025);v.co.z+=random.uniform(-.013,.013)
# Loose rocks and clumps frame terrace, never obscure architecture
for i in range(48):
 x=random.choice([-1,1])*random.uniform(2.5,6.0);y=random.uniform(-4,5)
 o=sphere('Weathered outcrop',(x,y,-.05),(random.uniform(.12,.45),random.uniform(.15,.4),random.uniform(.12,.35)),stone,'land',10);o.rotation_euler=(.2,.3,random.random()*3)
# Batched thin grass blades mesh
vs=[];fs=[]
for i in range(120):
 x=random.uniform(-7,7);y=random.uniform(-5,7)
 if abs(x)<2.6 and y<2.6:continue
 for j in range(9):
  a=Vector((x+random.uniform(-.12,.12),y+random.uniform(-.12,.12),-.015));h=random.uniform(.12,.45);dx=random.uniform(-.15,.15);dy=random.uniform(-.15,.15);n=len(vs);vs.extend([a+Vector((-.009,0,0)),a+Vector((.009,0,0)),a+Vector((dx,dy,h))]);fs.append((n,n+1,n+2))
mesh('Wild grass | batched blades',vs,fs,leafm[0],'land')
# Simple distant lake and rolling silhouettes are atmospheric context, not recovered terrain.
water=material('Lake | blue slate dusk',(.085,.13,.19),.18,.3)
cube('Distant lake',(0,32,-.035),(200,40,.025),water,'land')
for layer in range(3):
 verts=[];faces=[];yy=48+layer*12
 for i in range(81):
  x=-100+i*2.5;z=2+layer*1.1+1.8*math.sin(i*.21+layer)+.9*math.sin(i*.69+layer*2);verts.extend([(x,yy,-.2),(x,yy,z)])
 for i in range(80):faces.append((2*i,2*i+1,2*i+3,2*i+2))
 m=material('Distant ridge '+str(layer),(.12+layer*.035,.17+layer*.035,.24+layer*.035),1);mesh('Horizon ridge '+str(layer),verts,faces,m,'land')
# Light rig: blue overcast sky, low warm west light, warm inside bounce.
world=bpy.data.worlds.new('Blue hour | soft overcast');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.32,.48,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45

wn=world.node_tree.nodes;wl=world.node_tree.links;bg=wn.get('Background')
tc=wn.new('ShaderNodeTexCoord');sep=wn.new('ShaderNodeSeparateXYZ');wl.new(tc.outputs['Normal'],sep.inputs[0])
ramp=wn.new('ShaderNodeValToRGB');ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for i,(pos,col) in enumerate([(0,(.65,.41,.22,1)),(.08,(.35,.40,.50,1)),(.38,(.12,.20,.33,1)),(1,(.075,.13,.24,1))]):
 e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=col
neg=wn.new('ShaderNodeMath');neg.operation='MULTIPLY';neg.inputs[1].default_value=-1;wl.new(sep.outputs['Z'],neg.inputs[0]);wl.new(neg.outputs[0],ramp.inputs[0]);noise=wn.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6;noise.inputs['Detail'].default_value=5;noise.inputs['Roughness'].default_value=.7;wl.new(tc.outputs['Normal'],noise.inputs['Vector'])
cloud=wn.new('ShaderNodeValToRGB');cloud.color_ramp.elements[0].position=.28;cloud.color_ramp.elements[0].color=(.20,.25,.34,1);cloud.color_ramp.elements[1].position=.75;cloud.color_ramp.elements[1].color=(.78,.82,.90,1);wl.new(noise.outputs['Fac'],cloud.inputs[0])
mix=wn.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.7;wl.new(ramp.outputs[0],mix.inputs[1]);wl.new(cloud.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],bg.inputs[0]);bg.inputs[1].default_value=.7

def light(name,typ,loc,energy,color,size=1,target=None):
 d=bpy.data.lights.new(name,typ);d.energy=energy;d.color=color
 if typ=='AREA':d.shape='DISK';d.size=size
 elif typ=='POINT':d.shadow_soft_size=size
 o=bpy.data.objects.new(name,d);C['light'].objects.link(o);o.location=loc
 if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 return o
light('Large cool sky','AREA',(1,-2,9),750,(.57,.70,1),8,(0,0,0))
light('Sunset opening','AREA',(-6,-4,4),650,(1,.60,.27),6,(0,0,1))
light('Opal pendant light','POINT',(0,-.55,2.75),95,(1,.57,.22),.20)
light('Soft interior warmth','AREA',(0,.4,3.5),110,(1,.55,.20),1.8,(0,.7,.4))
# Proportion refinement from pixel comparison: shallow elliptical barrel, not assumed semicircle.
# Map the structural envelope into a 1.90m eave height + 1.248m roof rise above terrace.
def refined_z(z):
 return F+(z-F)*(1.90/(S-F)) if z<=S else F+1.90+(z-S)*.78
bpy.context.view_layer.update()
for key in ['frame','metal','glass','panels','bench','plants']:
 for o in C[key].objects:
  if o.type!='MESH':continue
  matrix=o.matrix_world.copy();inverse=matrix.inverted()
  for v in o.data.vertices:
   w=matrix @ v.co;w.z=refined_z(w.z);v.co=inverse @ w
# Keep the globe round and its low point 2.11m above the terrace.
# Only shorten the cord to meet the revised roof underside.
for o in C['light'].objects:
 if o.name.startswith('Pendant braided cord'):
  mat=o.matrix_world.copy();inv=mat.inverted()
  for v in o.data.vertices:
   w=mat @ v.co
   if w.z>3.5:w.z=3.49
   v.co=inv @ w
 elif o.name=='Soft interior warmth':o.location.z=3.30
# Cameras
camd=bpy.data.cameras.new('Concept match • 52mm');cam=bpy.data.objects.new('CAM | concept three-quarter',camd);C['camera'].objects.link(cam);cam.location=(6.8,-11.4,3.0);target=Vector((0,-.15,1.60));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=54;bpy.context.scene.camera=cam
camd.dof.use_dof=False
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=2;scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6;scene.cycles.transparent_max_bounces=8;scene.cycles.sample_clamp_indirect=2;scene.cycles.sample_clamp_direct=10;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.3
# Embedded guide + loaded, packed concept are portable without changing mesh visibility.
img=bpy.data.images.load(str(ROOT/'reference/gpt_image_concept.png'));img.pack();img.use_fake_user=True
text=bpy.data.texts.new('READ ME | Concept-to-geometry');text.use_fake_user=True;text.write('Original procedural study from one GPT Image concept. Dimensions and hidden geometry are inferred, NOT surveyed. No load, wind, glazing safety, waterproofing or code certification. Footprint 3.2 x 3.2 m; floor +0.42m; arch spring 2.32m; crown 3.568m. Front opening between jamb x=-0.65 and right post x=1.6. See external README.md and checks.json. All materials procedural, no external textures.\n')
# Camera view in saved startup for inspection
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=300
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
# Verifiable geometric checks: simple modeled relationships, not engineering checks.
checks={'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'inferred_dimensions_m':{'width':3.2,'depth':3.2,'floor_level':F,'spring_line':F+1.90,'crown':F+1.90+R*.78},'entrance_clear_width_m':R-.07-(DX+.08),'entrance_arch_height_at_left_jamb_m':refined_z(S+math.sqrt(R*R-(DX+.08)**2)-.07)-F,'posts_bottom_matches_floor':all(abs(min((o.matrix_world @ v.co).z for v in o.data.vertices)-F)<1e-5 for o in C['frame'].objects if ' | post ' in o.name),'render_engine':'Cycles CPU','threads':2,'denoising':False,'limits':['No structural, code, drainage, foundation, thermal or fabrication validation','Single-image inferred geometry; no exact CAD recovery','Landscape is a procedural setting, not geographic reconstruction']}
assert checks['entrance_clear_width_m']>2
assert checks['entrance_arch_height_at_left_jamb_m']>2.9
checks['entrance_minimum_headroom_m']=refined_z(S+math.sqrt(R*R-(R-.07)**2)-.07)-F
checks['pendant_low_point_above_floor_m']=2.77-.24-F
checks['bench_planter_gap_m']=.78-.17/2-(.55+.06/2)
assert checks['bench_planter_gap_m']>0
assert checks['posts_bottom_matches_floor']
(ROOT/'checks.json').write_text(json.dumps(checks,indent=2))
preview='--preview' in sys.argv
if preview:scene.render.resolution_percentage=50;scene.cycles.samples=48
scene.render.filepath=str(ROOT/'renders'/('preview.png' if preview else '05_final.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Glass_Refuge.blend'),compress=True)
bpy.ops.render.render(write_still=True)
