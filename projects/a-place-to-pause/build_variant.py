"""Seeded terrain postcard. Run: blender -b -t 2 --python build_variant.py -- --seed 1105 --save-blend"""
import bpy, math, random, json, bisect, argparse, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import landscape
parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=1105);parser.add_argument('--save-blend',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
SEED=args.seed
PROFILE=json.loads((OUT/'profiles.json').read_text())[str(SEED)];PARAMS=PROFILE['parameters']
random.seed(SEED)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
def mat(name,color,rough=0.9):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough
 return m
land=mat('Sage velvet meadow',(0.24,.29,.15)); roadmat=mat('Warm charcoal road',(.095,.087,.087)); gravel=mat('Ochre limestone shoulder',(.42,.34,.23)); stripe=mat('Faded ivory markings',(.78,.71,.48)); wood=mat('Weathered bench',(.22,.13,.073)); metal=mat('Bench legs',(.095,.105,.09))
def mesh(name,vs,fs,material):
 m=bpy.data.meshes.new(name); m.from_pydata(vs,[],fs); m.update(); o=bpy.data.objects.new(name,m); bpy.context.collection.objects.link(o); o.data.materials.append(material)
 for p in m.polygons:p.use_smooth=True
 return o
def cx(y):return 21*math.sin((y+25)/46)+.07*y
def dx(y):return 21/46*math.cos((y+25)/46)+.07
def natural(x,y):return landscape.natural(x,y,PARAMS)
def bed(y):return landscape.profile_height(y,PROFILE,PARAMS)
def width(y):return 3.0+4.5*math.exp(-((y-22)/9)**4)
def pos(y,u,lift=0):
 n=math.sqrt(1+dx(y)**2); return (cx(y)+u*n,y,bed(y)+lift)
def terrain(y,u):
 x,yy,z=pos(y,u); edge=3 if u<0 else width(y)
 d=max(0,abs(u)-edge-1.1); blend=min(1,d/40); blend=blend*blend*(3-2*blend)
 return (x,yy,z*(1-blend)+natural(x,yy)*blend)
ys=[-130+i*.75 for i in range(841)]
terrain_ys=ys+[508+i*8 for i in range(115)]
us=sorted(set([-220+i*2 for i in range(221)]+[-1200+i*20 for i in range(121)]+[-4.1,-3,0,3,4.1]))
vs=[terrain(y,u) for y in terrain_ys for u in us]; n=len(us)
fs=[(i*n+j,i*n+j+1,(i+1)*n+j+1,(i+1)*n+j) for i in range(len(terrain_ys)-1) for j in range(n-1)]
mesh('Roadbed blended meadow',vs,fs,land)
def ribbon(name,left,right,lift,material,start=-130,end=500,step=.75):
 yy=[start+i*step for i in range(int((end-start)/step)+1)]
 verts=[pos(y,u(y),lift) for y in yy for u in (left,right)]
 faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(yy)-1)]
 return mesh(name,verts,faces,material)
shoulder=ribbon('Blended limestone shoulder',lambda y:-4,lambda y:width(y)+1,.018,gravel)
road=ribbon('Road and viewpoint apron',lambda y:-3, width,.045,roadmat)
for side in [-1,1]:ribbon('Quiet edge line',lambda y:side*2.62-.055,lambda y:side*2.62+.055,.058,stripe)
for y in range(-128,497,9):ribbon('Short faded center dash',lambda y:-.065,lambda y:.065,.058,stripe,y,y+3,.5)
# Continuous terrain avoids overlapping backdrop sheets. Distant color washes to lavender.
nodes=land.node_tree.nodes; links=land.node_tree.links
geo=nodes.new('ShaderNodeNewGeometry'); sep=nodes.new('ShaderNodeSeparateXYZ'); links.new(geo.outputs['Position'],sep.inputs[0])
mapper=nodes.new('ShaderNodeMapRange'); mapper.inputs['From Min'].default_value=160; mapper.inputs['From Max'].default_value=650;links.new(sep.outputs['Y'],mapper.inputs[0])
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.24,.29,.15,1);ramp.color_ramp.elements[1].color=(.32,.32,.40,1);links.new(mapper.outputs[0],ramp.inputs[0]);links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
def cube(name,loc,scale,ma,angle=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;o.rotation_euler[2]=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 bevel=o.modifiers.new('Soft edges','BEVEL');bevel.width=.04;bevel.segments=2
 return o
# Viewpoint bench sits on the actual widened apron, faces the open hills.
y=22;x,yy,z=pos(y,6.3,.045); a=-math.atan(dx(y))
for off in [-.22,0,.22]:cube('Bench seat slat',(x,yy+off,z+.55),(2.1,.17,.09),wood,a)
for off in [-.73,.73]:cube('Bench foot',(x+off,yy,z+.28),(.10,.5,.55),metal,a)
cube('Bench back',(x,yy+.26,z+.96),(2.1,.10,.43),wood,a)
# Low gravel boulders mark the far rim; no guardrails implying real safety approval.
for y in [15,19,26,30]:
 x,yy,z=pos(y,width(y)+.45,.03);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.3,location=(x,yy,z+.13));o=bpy.context.object;o.name='Viewpoint boundary stone';o.scale=(1.3,.8,.7);o.data.materials.append(gravel)
# Sparse natural accents well outside road corridor.
for i in range(80):
 y=random.uniform(-95,190);u=random.choice([-1,1])*random.uniform(14,120);x,yy,z=terrain(y,u)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.3,1.1),location=(x,yy,z+.12));o=bpy.context.object;o.name='Meadow stone';o.scale=(1.4,1,.65);o.data.materials.append(gravel)
world=bpy.data.worlds.new('Apricot dusk');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.44,.32,.27,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7;bpy.context.scene.world=world
bpy.ops.object.light_add(type='SUN',location=(-90,100,100));sun=bpy.context.object;sun.name='Last amber daylight';sun.data.energy=2.8;sun.data.color=(1,.69,.43);sun.data.angle=.13;sun.rotation_euler=(math.radians(63),math.radians(-20),math.radians(-110))
bpy.ops.object.camera_add(location=(48,-95,43));cam=bpy.context.object;cam.name='Evening overlook camera';target=Vector((5,95,15));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=42;cam.data.clip_end=2000;bpy.context.scene.camera=cam
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=600;s.render.resolution_y=400;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/f'seed_{SEED}.png');s.view_settings.view_transform='AgX'
# Numerical checks concern virtual design geometry, not road engineering compliance.
assert all(p.normal.z>0 for p in road.data.polygons)
grades=[];curv=[];clear=[]
for y in ys[1:-1]:
 grades.append(abs((bed(y+.01)-bed(y-.01))/.02)/math.sqrt(1+dx(y)**2))
 curv.append(abs(-21/46**2*math.sin((y+25)/46))/(1+dx(y)**2)**1.5)
 for u in [-3,-1,0,1,3]:clear.append(pos(y,u,.045)[2]-terrain(y,u)[2])
report={'seed':SEED,'units':'1 Blender unit = 1 virtual metre','road_width_m':6,'viewpoint_max_width_m':10.5,'terrain_blend_width_m':40,'centerline_samples':len(ys),'upward_road_faces':len(road.data.polygons),'inverted_road_faces':sum(p.normal.z<=0 for p in road.data.polygons),'sampled_clearance_min_m':min(clear),'sampled_clearance_max_m':max(clear),'maximum_virtual_grade_percent':max(grades)*100,'maximum_virtual_curvature_per_m':max(curv),'minimum_virtual_curve_radius_m':1/max(curv),'scope':'Virtual landscape only; not civil-road safety or engineering standards. Clearance checks sample analytic bed; no physical simulation.'}
earthwork=[terrain(y,u)[2]-natural(*terrain(y,u)[:2]) for y in ys for u in range(-50,51)]
report.update({'earthwork_sample_count':len(earthwork),'maximum_cut_m':max(0,-min(earthwork)),'maximum_fill_m':max(0,max(earthwork)),'road_profile':'6 percent virtual aesthetic cap; constrained smooth fit plus cap-preserving slope smoothing; 40 m earthwork transition'})
(OUT/f'validation_{SEED}.json').write_text(json.dumps(report,indent=2)+'\n')
from mathutils.bvhtree import BVHTree
terr=bpy.data.objects['Roadbed blended meadow']
def bvh(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],all_triangles=False)
tb=bvh(terr);rb=bvh(road);gaps=[];miss=0
for f in road.data.polygons:
 for v in [f.center]+[road.data.vertices[i].co.lerp(f.center,.1) for i in f.vertices]:
  top=Vector((v.x,v.y,100));th=tb.ray_cast(top,Vector((0,0,-1)))[0];rh=rb.ray_cast(top,Vector((0,0,-1)))[0]
  if th is None or rh is None:miss+=1
  else:gaps.append(rh.z-th.z)
report.update({'terrain_non_upward_faces':sum(f.normal.z<=0 for f in terr.data.polygons),'mesh_raycast_samples':len(gaps),'mesh_raycast_misses':miss,'mesh_clearance_min_m':min(gaps),'mesh_clearance_max_m':max(gaps),'mesh_below_terrain_samples':sum(v<=0 for v in gaps),'terrain_parameters':PARAMS})
assert miss==0 and min(gaps)>0 and report['terrain_non_upward_faces']==0
(OUT/f'validation_{SEED}.json').write_text(json.dumps(report,indent=2)+'\n')
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
s['study_title']=f'Seeded Roadscapes / terrain seed {SEED}';s['seed']=SEED
if args.save_blend:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'seed_{SEED}.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('QUIET_ROAD_VALIDATION',json.dumps(report))
