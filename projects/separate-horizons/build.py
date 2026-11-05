"""Separate Horizons. Two inclined vessels, two independently horizontal surfaces."""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'probe'
N=192
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=96 if MODE=='probe' else 1024;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.005;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
s.render.resolution_x=760 if MODE=='probe' else 1600;s.render.resolution_y=570 if MODE=='probe' else 1200;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.35
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.77,.84,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.30

def mat(name,c,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
clay=mat('Warm white porcelain',(.72,.67,.55),.26)
stone=mat('Pale limestone supports',(.23,.27,.25),.85)
ground=mat('Quiet grey ground',(.44,.46,.44),.92)
water=mat('Clear pale green water',(.73,.91,.87),.045);p=water.node_tree.nodes['Principled BSDF'];p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333
absorb=water.node_tree.nodes.new('ShaderNodeVolumeAbsorption');absorb.inputs['Color'].default_value=(.30,.67,.57,1);absorb.inputs['Density'].default_value=.38;water.node_tree.links.new(absorb.outputs['Volume'],water.node_tree.nodes['Material Output'].inputs['Volume'])
# No texture maps or imported models.
def mesh(name,vs,fs,material,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 for f in me.polygons:f.use_smooth=smooth
 return o
profile=[(.0,.0),(.72,.0),(.92,.85),(.845,.85),(.70,.14),(.0,.14)]
solids=[];qa=[]
configs=[('I',(-1.30,0),18,90),('II',(1.30,0),-21,90)]
H=.73
for name,(x,y),deg,az in configs:
 axis=Vector((math.cos(math.radians(az)),math.sin(math.radians(az)),0));R=Matrix.Rotation(math.radians(deg),3,axis);origin=Vector((x,y,.72*math.sin(abs(math.radians(deg)))+.045))
 vs=[]
 for r,z in profile:
  for i in range(N):
   t=2*math.pi*i/N;vs.append(tuple(origin+R@Vector((r*math.cos(t),r*math.sin(t),z))))
 fs=[]
 for j in range(len(profile)-1):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 o=mesh('Vessel '+name,vs,fs,clay);b=o.modifiers.new('Small softened ceramic edges','BEVEL');b.width=.012;b.segments=3;o.modifiers.new('Ceramic normals','WEIGHTED_NORMAL');solids.append(o)
 # Analytic intersection of a horizontal surface and the straight inner conical wall.
 slope=(.845-.70)/(.85-.14);intercept=.70-slope*.14
 rim=[];bottom=[];local_heights=[]
 for i in range(N):
  t=2*math.pi*i/N;ct,st=math.cos(t),math.sin(t);a=R[2][0]*ct+R[2][1]*st
  z=(H-origin.z-a*intercept)/(R[2][2]+slope*a);r=intercept+slope*z-.0005;v=origin+R@Vector((r*ct,r*st,z));v.z=H;rim.append(tuple(v));local_heights.append(z)
  bottom.append(tuple(origin+R@Vector((.69*ct,.69*st,.15))))
 wvs=rim+bottom;wfs=[tuple(range(N)),tuple(range(2*N-1,N-1,-1))]
 for i in range(N):wfs.append((i,N+i,N+(i+1)%N,(i+1)%N))
 wo=mesh('Water '+name,wvs,wfs,water,False)
 for poly in wo.data.polygons[2:]:poly.use_smooth=True
 split=wo.modifiers.new('Smooth conical sides, flat horizontal surface','EDGE_SPLIT');split.split_angle=.5;split.use_edge_angle=True
 solids.append(wo)
 # Circular wedge supporting the entire inclined bottom, without floating intersections.
 n=R@Vector((0,0,1));pv=[];rad=.65
 for zlayer in [0,1]:
  for i in range(N):
   t=2*math.pi*i/N;dx=rad*math.cos(t);dy=rad*math.sin(t);z=.0 if zlayer==0 else origin.z-(n.x*dx+n.y*dy)/n.z
   pv.append((x+dx,y+dy,z))
 pf=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 for i in range(N):pf.append((i,(i+1)%N,N+(i+1)%N,N+i))
 ped=mesh('Inclined support '+name,pv,pf,stone,False);be=ped.modifiers.new('Stone edge','BEVEL');be.width=.008;be.segments=2;ped.modifiers.new('Stone normals','WEIGHTED_NORMAL');solids.append(ped)
 qa.append({'name':name,'inclination_degrees':deg,'water_global_height':H,'water_height_error':max(abs(v[2]-H) for v in rim),'local_water_height_range':[min(local_heights),max(local_heights)],'inner_floor_local_z':.14,'rim_local_z':.85,'rim_clearance_local':.85-max(local_heights),'support_min_z':min(v[2] for v in pv[N:])})
 assert min(local_heights)>.14 and max(local_heights)<.85
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.name='Ground';bpy.context.object.data.materials.append(ground)
target=Vector((0,0,.35))
for name,loc,power,size,color in [('Broad window',(-2,8,6),450,4,(1,.89,.72)),('Far soft fill',(-3,-4,6),320,4,(.72,.84,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.size=size;o.data.color=color;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
window=bpy.data.objects['Broad window'];window.data.shape='RECTANGLE';window.data.size_y=1.0
bpy.ops.object.camera_add(location=(0,-8,6.4));cam=bpy.context.object;cam.name='Still life camera';cam.data.type='ORTHO';cam.data.ortho_scale=5.8;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
bpy.context.view_layer.update();coords=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in solids for v in o.data.vertices]
qa={'vessels':qa,'frame_min_margin':min(min(v.x,1-v.x,v.y,1-v.y) for v in coords),'water_model':'Analytic horizontal top; inner boundary inset 0.0005 at top and 0.01 at floor to clear beveled ceramic; no dynamics simulation.','objects':len(s.objects),'mode':MODE}
(P/'geometry-qa.json').write_text(json.dumps(qa,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'Separate-Horizons.blend'))
