"""한 자리에서만 원: a perspective-aligned original virtual sculpture."""
import bpy,math,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'probes'
if mode=='film':
 revision=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 marker=ROOT/'frame_revision.json';folder=ROOT/'frames'
 if marker.exists():
  if json.loads(marker.read_text())['source_sha256']!=revision:raise RuntimeError('Source changed: archive frames and frame_revision.json before rerendering.')
 else:
  if folder.exists() and any(folder.glob('*.png')):raise RuntimeError('Unversioned frames exist: archive them before rendering.')
  marker.write_text(json.dumps({'source_sha256':revision,'resolution':[640,640],'samples':24,'fps':12},indent=2)+'\n')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.max_bounces=5;s.cycles.use_animated_seed=False
s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True
s.render.resolution_x=720;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.view_settings.view_transform='AgX';s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.9,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

def mat(name,c,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough;return m
green=mat('Deep green lacquer',(.018,.21,.16),.43);lime=mat('Acid yellow accent',(.70,.88,.035),.6);back=mat('Quiet green edge',(.035,.11,.085),.7);bg=mat('Warm off white cyclorama',(.77,.74,.66),.9)
# An all-around curved backdrop avoids a visible open edge during the wide orbit.
profile=[(8,0)]+[(8+3*math.sin(t),3*(1-math.cos(t))) for t in [i*math.pi/2/48 for i in range(1,49)]]+[(11,20)]
N=128;verts=[(0,0,0)]
for radius,z in profile:
 for j in range(N):
  a=math.tau*j/N;verts.append((radius*math.cos(a),radius*math.sin(a),z))
faces=[(0,1+j,1+(j+1)%N) for j in range(N)]
for i in range(len(profile)-1):
 for j in range(N):
  a=1+i*N+j;b=1+i*N+(j+1)%N;faces.append((a,a+N,b+N,b))
mesh=bpy.data.meshes.new('Surrounding cyclorama mesh');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Continuous backdrop',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(bg)
for p in mesh.polygons:p.use_smooth=True
# Camera C=(0,-10,2), target plane distance D=10. Each front-face vertex is
# C + (t/D)*(P-C). Perspective projection from C is unchanged by t.
C=Vector((0,-10,2));D=10.;depths=[8.0,11.6,9.4,13.0,7.2,10.8,12.4,8.8];rin=.81;rout=1.25;segments=[];records=[]
for k,t in enumerate(depths):
 a0=math.radians(k*45+3);a1=math.radians((k+1)*45-3);vs=[];uvs=[]
 for j in range(25):
  a=a0+(a1-a0)*j/24
  for r in [rin,rout]:
   x=r*math.cos(a);z=r*math.sin(a)
   vs.append((x*t/D,-10+t,2+z*t/D));uvs.append((x,z))
 fs=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(24)]
 me=bpy.data.meshes.new('Arc front mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(f'Arc {k+1:02d}',me);bpy.context.collection.objects.link(o);o.data.materials.append(lime if k in [1,5] else green);o.data.materials.append(back)
 solid=o.modifiers.new('Back extrusion','SOLIDIFY');solid.thickness=.13*t/D;solid.offset=-1;solid.material_offset=1;solid.material_offset_rim=1
 # Normals face the privileged camera. Mesh order gives -Y for the first arc.
 bevel=o.modifiers.new('Very small edge radius','BEVEL');bevel.width=.008*t/D;bevel.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 segments.append(o);records.append({'arc':k+1,'camera_forward_distance':t,'scale':t/D,'angle_degrees':[k*45+3,(k+1)*45-3]})
bpy.ops.object.camera_add(location=C);cam=bpy.context.object;cam.name='Privileged view then orbit';cam.data.type='PERSP';cam.data.lens=80;cam.data.sensor_width=36;target=Vector((0,0,2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
# Verify base-front vertices against reference-plane points before modifiers.
bpy.context.view_layer.update();maxerr=0
for k,(o,t) in enumerate(zip(segments,depths)):
 for vi,v in enumerate(o.data.vertices):
  actual=world_to_camera_view(s,cam,o.matrix_world@v.co)
  a=math.radians(k*45+3)+(math.radians(39))*(vi//2)/24
  r=rin if vi%2==0 else rout
  reference=Vector((r*math.cos(a),0,2+r*math.sin(a)))
  ref=world_to_camera_view(s,cam,reference)
  maxerr=max(maxerr,abs(actual.x-ref.x),abs(actual.y-ref.y))
assert maxerr<1e-6,maxerr
for name,loc,power,size,color in [('Large soft key',(-4,-5,8),1250,4,(1,.91,.76)),('Broad cool fill',(5,1,6),450,5,(.72,.85,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.size=size;l.data.color=color;l.rotation_euler=(target-l.location).to_track_quat('-Z','Y').to_euler()
def pose(f):
 # Hold the privileged view, orbit smoothly, then hold the revealed arrangement.
 if f<=24:u=0
 elif f>=72:u=1
 else:u=(f-24)/48;u=u*u*(3-2*u)
 desired_lens=80-32*u
 a=math.radians(70)*u;cam.location=(10*math.sin(a),-10*math.cos(a),2+1.5*u);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();extent=0
 for o,t in zip(segments,depths):
  for v in o.data.vertices:
   for back_depth in [0,.13*t/D]:
    local=inv@(v.co+Vector((0,back_depth,0))-cam.location)
    extent=max(extent,abs(local.x/-local.z),abs(local.y/-local.z))
 cam.data.lens=min(desired_lens,.43*cam.data.sensor_width/extent)
 return u
s.frame_start=1;s.frame_end=96;s.render.fps=12
last_lens=80
for f in range(1,97):
 pose(f);cam.data.lens=min(cam.data.lens,last_lens);last_lens=cam.data.lens;cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);cam.data.keyframe_insert(data_path='lens',frame=f)
for owner in [cam,cam.data]:
 for fc in owner.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
if mode=='film':s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=24
s.frame_set(1);s.render.filepath='//frames/frame_';bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'One-View-Circle.blend'),compress=True)
(ROOT/'projection_check.json').write_text(json.dumps({'camera_origin':list(C),'reference_distance':D,'maximum_normalized_xy_error':maxerr,'checked_base_vertices':sum(len(o.data.vertices) for o in segments),'excludes':'Bevel and solidify silhouette, shading, and other viewpoints','segments':records},indent=2)+'\n')
frames=ROOT/'frames';frames.mkdir(exist_ok=True)
def render(f,name):
 s.frame_set(f);s.render.filepath=str(ROOT/name);bpy.ops.render.render(write_still=True)
 p=Path(s.render.filepath);raw=p.read_bytes();out=bytearray(raw[:8]);off=8
 while off<len(raw):
  n=int.from_bytes(raw[off:off+4],'big');kind=raw[off+4:off+8]
  if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out.extend(raw[off:off+n+12])
  off+=n+12
 p.write_bytes(out)
if mode=='probes':
 for f,name in [(1,'01-privileged.png'),(48,'02-between.png'),(72,'03-revealed.png')]:render(f,name)
elif mode=='film':
 s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=24
 for f in [1]+list(range(25,73)):
  p=frames/f'frame_{f:04d}.png'
  if not p.exists():render(f,str(p.relative_to(ROOT)))
 for f in range(1,97):
  p=frames/f'frame_{f:04d}.png'
  if not p.exists():p.write_bytes((frames/('frame_0001.png' if f<=24 else 'frame_0072.png')).read_bytes())
else:raise ValueError(mode)
