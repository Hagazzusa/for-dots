"""문턱에 남은 빛: original 12-second silent 3D study from Last Umbrella."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
source=Path(args[0]).resolve();probe='--probe' in args
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
s.cycles.samples=24;s.cycles.use_denoising=False;s.cycles.use_animated_seed=False
s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.08
bpy.data.objects['Cloudy dusk'].data.energy=65;bpy.data.objects['Soft side light'].data.energy=25
lamp=bpy.data.objects['Amber porch lamp'].data
bs=bpy.data.materials['Milk glass warm light'].node_tree.nodes['Principled BSDF']
for frame,power,emission in [(1,55,3),(49,0,0),(73,55,3)]:
 lamp.energy=power;lamp.keyframe_insert(data_path='energy',frame=frame)
 bs.inputs['Emission Strength'].default_value=emission;bs.inputs['Emission Strength'].keyframe_insert(data_path='default_value',frame=frame)
# The switch changes instantly; the final camera move eases in and out.
for owner in [lamp,bpy.data.materials['Milk glass warm light'].node_tree]:
 if owner.animation_data and owner.animation_data.action:
  for fc in owner.animation_data.action.fcurves:
   for key in fc.keyframe_points:key.interpolation='CONSTANT'
cam=s.camera;initial=cam.location.copy();scale=cam.data.ortho_scale
for frame,delta,ortho in [(1,(0,0,0),scale),(96,(0,0,0),scale),(144,(.1,-.75,-.4),4.1)]:
 cam.location=initial+Vector(delta);cam.keyframe_insert(data_path='location',frame=frame)
 cam.data.ortho_scale=ortho;cam.data.keyframe_insert(data_path='ortho_scale',frame=frame)
for owner in [cam,cam.data]:
 for fc in owner.animation_data.action.fcurves:
  for key in fc.keyframe_points:key.interpolation='BEZIER';key.handle_left_type='AUTO_CLAMPED';key.handle_right_type='AUTO_CLAMPED'
s.render.fps=12;s.frame_start=1;s.frame_end=144;s.frame_set(1)
s.render.filepath='//frames/frame_';bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Light-on-the-Threshold.blend'),compress=True)
frames=ROOT/'frames';frames.mkdir(exist_ok=True)
# Two static states cover seconds 0–8. Only moving-camera frames need new renders.
render_frames=[1,49,144] if probe else [1,49]+list(range(97,145))
for frame in render_frames:
 path=frames/f'frame_{frame:04d}.png'
 if not probe and path.exists():continue
 s.frame_set(frame);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 raw=path.read_bytes();out=bytearray(raw[:8]);off=8
 while off<len(raw):
  n=int.from_bytes(raw[off:off+4],'big');kind=raw[off+4:off+8]
  if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out.extend(raw[off:off+n+12])
  off+=n+12
 path.write_bytes(out)
if probe:raise SystemExit(0)
# Reuse exact unchanged renders, not interpolated image geometry.
for frame in list(range(2,49))+list(range(50,97)):
 target=frames/f'frame_{frame:04d}.png';original=frames/('frame_0049.png' if frame<73 and frame>=49 else 'frame_0001.png')
 if not target.exists():target.write_bytes(original.read_bytes())
(ROOT/'render_conditions.json').write_text(json.dumps({'blender':bpy.app.version_string,'duration_seconds':12,'fps':12,'frames':144,'rendered_states':50,'resolution':[640,640],'samples':24,'denoiser':'FFmpeg hqdn3d mild spatial-temporal video filter; Blender denoising unavailable','sound':False,'camera':'Original orthographic geometry, translation and scale animated in final 4 seconds','source_scene_modified':False},indent=2)+'\n')
