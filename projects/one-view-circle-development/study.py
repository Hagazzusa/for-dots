import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
SRC=P.parent/'one-view-circle'/'One-View-Circle.blend'
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;cam=s.camera
cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='PERSP'
target=Vector((0,0,2));arcs=[o for o in s.objects if o.name.startswith('Arc ')]
s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True;s.cycles.use_animated_seed=False
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'check'
def angle_at(t):
 if t<=4:return 0.
 if t<11:a,b,lo,hi=0,55,4,11
 elif t<14:return 55.
 elif t<24:a,b,lo,hi=55,-35,14,24
 elif t<28:a,b,lo,hi=-35,0,24,28
 else:return 0.
 u=(t-lo)/(hi-lo);u=u*u*(3-2*u)
 return a+(b-a)*u
def pose(t,lens=48):
 a=math.radians(angle_at(t));cam.location=(10*math.sin(a),-10*math.cos(a),2);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;bpy.context.view_layer.update()
# Modifier-evaluated geometry ensures bevel and back thickness are included.
points=[];deps=bpy.context.evaluated_depsgraph_get()
for o in arcs:
 ev=o.evaluated_get(deps);mesh=ev.to_mesh();points.extend([ev.matrix_world@v.co for v in mesh.vertices]);ev.to_mesh_clear()
if mode=='check':
 reports=[]
 for lens in [48,55,64]:
  worst=1.;at=0.;behind=False
  for k in range(769):
   t=k/24;pose(t,lens)
   for point in points:
    v=world_to_camera_view(s,cam,point);margin=min(v.x,1-v.x,v.y,1-v.y)
    if margin<worst:worst=margin;at=t
    behind=behind or v.z<=0
  reports.append({'lens_mm':lens,'minimum_normalized_margin':worst,'worst_time_seconds':at,'behind_camera':behind})
 (P/'framing-study.json').write_text(json.dumps({'source_sha256':source_hash,'evaluated_vertices':len(points),'camera_height':2,'duration':32,'reports':reports},indent=2)+'\n');print(reports)
else:
 fps=12;s.render.fps=fps;s.frame_start=1;s.frame_end=32*fps
 s.render.resolution_x=320 if mode=='preview' else 480;s.render.resolution_y=s.render.resolution_x;s.cycles.samples=4 if mode=='preview' else 8;s.cycles.use_denoising=False
 for f in range(1,s.frame_end+1):
  pose((f-1)/fps);cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
 for fc in cam.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 s.frame_set(1);s.render.filepath='//preview/frame_';bpy.ops.wm.save_as_mainfile(filepath=str(P/'Passing-the-Circle-preview.blend'),compress=True)
 folder=P/'preview';folder.mkdir(exist_ok=True)
 revision=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();marker=P/'preview-revision.json'
 if marker.exists() and any(folder.glob('frame_*.png')):assert json.loads(marker.read_text())['source_sha256']==revision
 else:marker.write_text(json.dumps({'source_sha256':revision,'original_scene_sha256':source_hash,'fps':fps,'resolution':s.render.resolution_x,'samples':s.cycles.samples},indent=2))
 def render(f,path):
  s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 if mode=='probes':
  for f in [1,85,133,217,289,337]:render(f,P/f'probe-{f:03d}.png')
 elif mode=='preview':
  cached={}
  for f in range(1,s.frame_end+1):
   angle=round(angle_at((f-1)/fps),10);out=folder/f'frame_{f:04d}.png'
   if out.exists():cached[angle]=out;continue
   if angle in cached:out.write_bytes(cached[angle].read_bytes())
   else:render(f,out);cached[angle]=out
 else:raise ValueError(mode)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_hash
