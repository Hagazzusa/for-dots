"""마지막 우산: external-asset-free, editable procedural Blender still."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
PREVIEW='--preview' in sys.argv
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=20 if PREVIEW else 192
s.cycles.use_denoising=False; s.cycles.max_bounces=6
s.render.threads_mode='FIXED'; s.render.threads=3
s.render.resolution_x=650 if PREVIEW else 1300; s.render.resolution_y=650 if PREVIEW else 1300; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.view_settings.view_transform='AgX'; s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.25,.4,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4

def mat(name,col,rough=.65,metal=0,emit=0):
 m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
 if emit: b.inputs['Emission Color'].default_value=(*col,1); b.inputs['Emission Strength'].default_value=emit
 return m
stone=mat('Blue grey stone',(.19,.25,.27)); wall=mat('Old teal limewash',(.13,.24,.24)); mortar=mat('Dark joints',(.06,.11,.12)); wood=mat('Worn ochre wood',(.32,.19,.085)); iron=mat('Painted iron',(.035,.055,.06),.4,.3); amber=mat('Umbrella terracotta',(.65,.19,.06),.78); pale=mat('Umbrella faded orange',(.78,.30,.095),.78); seam=mat('Stitched ribs',(.31,.075,.027),.7); water=mat('Pooled water',(.07,.15,.19),.12,.35); glow=mat('Milk glass warm light',(1,.69,.32),.35,0,3); paper=mat('Unmarked folded paper',(.6,.58,.43)); sky=mat('Distant wet lane',(.065,.10,.13),.68)
def box(name,loc,dim,ma,b=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 if b: m=o.modifiers.new('Rounded edges','BEVEL'); m.width=b; m.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def curve(name,pts,r,ma):
 c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=2; c.bevel_depth=r; c.bevel_resolution=3; p=c.splines.new('POLY'); p.points.add(len(pts)-1)
 for v,co in zip(p.points,pts): v.co=(*co,1)
 o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(ma); return o

def cylinder(name,loc,r,depth,ma):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(ma); return o
box('Continuous lane',(0,0,-.15),(200,200,.2),sky)
box('Raised porch',(0,.3,.015),(3.8,2.6,.13),stone)
for i in range(-3,4):
 for j in range(4):
  x=i*.52; y=-.67+j*.6
  box('Individual paving stone',(x,y,.095),(.50,.58,.03),stone,.009)
box('Back wall',(0,1.55,1.39),(3.85,.16,2.82),wall)
box('Left return',(-1.86,.55,1.39),(.13,2.0,2.82),wall)
# A recessed wooden door is intentionally closed, with no anonymous lettering.
box('Door shadow',(.85,1.452,1.16),(1.24,.03,2.18),mortar)
for i in range(6): box('Door vertical board',(.35+i*.2,1.425,1.16),(.187,.035,2.09),wood,.008)
for x in [.23,1.47]: box('Door frame',(x,1.38,1.16),(.09,.09,2.25),iron,.01)
box('Door lintel',(.85,1.38,2.29),(1.32,.09,.09),iron,.01)
curve('Door pull',[(1.25,1.38,1.05),(1.25,1.30,1.05),(1.25,1.30,1.20),(1.25,1.38,1.20)],.014,iron)
# Partial roof and two beams make a covered threshold without hiding the subject.
box('Shelter roof',(0,.55,2.86),(4.1,2.45,.12),iron)
for x in [-1.62,1.62]: box('Roof bracket',(x,1.15,2.74),(.08,.65,.12),wood)
# Small bench, actual feet contact porch: .11 + .37/2 = .295.
for x in [-1.35,-.53]:
 for y in [.85,1.15]: box('Bench foot',(x,y,.295),(.055,.055,.37),iron,.009)
for y in [.83,1.0,1.17]: box('Bench seat',(-.94,y,.5),(1.12,.15,.06),wood,.013)
box('Folded cloth',(-1.18,1.02,.553),(.36,.29,.045),paper,.012)
# Umbrella: 8 scalloped cloth panels, coherent convex dome and continuous ribs.
# Root on same porch plane. Shaft and hook are supported by a discreet iron stand.
cx,cy=-.45,-.15
cylinder('Umbrella stand base',(cx,cy,.14),.16,.08,iron)
curve('Umbrella shaft',[(cx,cy,.18),(cx,cy,1.49)],.012,iron)
curve('Curved umbrella handle',[(cx+.085*(1-math.cos(t)),cy,.35-.085*math.sin(t)) for t in [i*math.pi/24 for i in range(25)]],.018,wood)
R=.69; top=1.47
for k in range(8):
 verts=[]; faces=[]
 for ir in range(13):
  t=ir/12
  for ia in range(9):
   f=ia/8; a=(k+f)*math.tau/8
   r=R*t*(1-.065*math.sin(math.pi*f)*t**5)
   z=top-.36*t*t-.045*math.sin(math.pi*f)*t**5
   verts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
 for ir in range(12):
  for ia in range(8):
   v=ir*9+ia; faces.append((v,v+1,v+10,v+9))
 mesh=bpy.data.meshes.new('Radial cloth panel'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('Umbrella cloth %d'%k,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(amber if k%2 else pale)
 for p in mesh.polygons: p.use_smooth=True
 sol=o.modifiers.new('Cloth thickness','SOLIDIFY'); sol.thickness=.002
 a=k*math.tau/8
 curve('Umbrella rib',[(cx+R*t*math.cos(a),cy+R*t*math.sin(a),top-.36*t*t+.003) for t in [i/24 for i in range(25)]],.004,seam)
 curve('Umbrella edge',verts[-9:],.006,seam)
cylinder('Umbrella finial',(cx,cy,1.5),.017,.09,wood)
# Shallow, irregular water mesh on the lane. Reflection remains stylized, not a fluid simulation.
def puddle(name,x,y,rx,ry):
 verts=[(x,y,-.046)]
 for i in range(96):
  a=i*math.tau/96; r=1+.07*math.sin(5*a)+.035*math.cos(9*a); verts.append((x+rx*r*math.cos(a),y+ry*r*math.sin(a),-.046))
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],[(0,i+1,(i+1)%96+1) for i in range(96)]); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(water)
puddle('Threshold rainwater',.30,-1.49,1.4,.43)
puddle('Small separate pool',-1.50,-1.2,.22,.13)
# Wall lamp has a visible bracket and casts a small warm pool.
curve('Lamp bracket',[(-1.03,1.44,2.4),(-1.03,1.08,2.4),(-1.03,1.08,2.24)],.019,iron)
cylinder('Lamp shade',(-1.03,1.08,2.22),.17,.06,iron)
cylinder('Lamp milk glass',(-1.03,1.08,2.14),.10,.13,glow)
bpy.ops.object.light_add(type='AREA',location=(-1.03,1.08,2.05)); l=bpy.context.object; l.name='Amber porch lamp'; l.data.energy=55; l.data.color=(1,.57,.25); l.data.size=.35
for name,loc,energy,col,size,target in [('Cloudy dusk',(0,-3,6),380,(.52,.7,1),5,(0,0,.6)),('Soft side light',(4,-1,3),150,(.59,.78,1),4,(0,0,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.color=col; l.data.size=size; l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5.5,-8,3.3)); cam=bpy.context.object; target=Vector((0,.25,1.12)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.5; cam.location+=(cam.location-target).normalized()*18; s.camera=cam
s['scale_note']='Approximate metres; porch surface .11, bench seat .53, door 2.09, umbrella diameter 1.38.'
s.render.filepath='//Last-Umbrella.png'; bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Last-Umbrella.blend')); s.render.filepath=str(ROOT/('preview.png' if PREVIEW else 'Last-Umbrella.png')); bpy.ops.render.render(write_still=True)
p=Path(s.render.filepath); raw=p.read_bytes(); out=bytearray(raw[:8]); off=8
while off<len(raw):
 n=int.from_bytes(raw[off:off+4],'big'); kind=raw[off+4:off+8]
 if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}: out.extend(raw[off:off+n+12])
 off+=n+12
p.write_bytes(out)
(ROOT/'validation.json').write_text(json.dumps({'blender':bpy.app.version_string,'objects':len(s.objects),'samples':s.cycles.samples,'preview':PREVIEW,'external_images':sum(bool(i.filepath) for i in bpy.data.images),'orthographic':True},indent=2))
