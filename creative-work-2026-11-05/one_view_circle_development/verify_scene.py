import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
original=P.parent/'one_view_circle'/'One-View-Circle.blend'
def snapshot():
 result={}
 for o in bpy.context.scene.objects:
  if o.type=='CAMERA':continue
  d={'type':o.type,'matrix':list(sum((list(r) for r in o.matrix_world),[])),'animated':o.animation_data is not None}
  if o.type=='MESH':
   d['vertices']=[list(v.co) for v in o.data.vertices];d['polygons']=[list(p.vertices) for p in o.data.polygons]
   d['material_colors']=[list(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value) for m in o.data.materials]
  if o.type=='LIGHT':d.update(energy=o.data.energy,color=list(o.data.color),size=o.data.size)
  result[o.name]=d
 return result
bpy.ops.wm.open_mainfile(filepath=str(original));before=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(P/'Passing-the-Circle-preview.blend'));after=snapshot();assert before==after
s=bpy.context.scene;cam=s.camera;states=[]
for f in range(1,385):
 s.frame_set(f);assert abs(cam.location.z-2)<1e-6;assert abs(cam.data.lens-48)<1e-6
 if f in [1,133,238,289,384]:states.append({'frame':f,'location':list(cam.location),'lens':cam.data.lens})
assert states[0]['location']==states[-1]['location']
assert (P/'preview/frame_0001.png').read_bytes()==(P/'preview/frame_0384.png').read_bytes()
assert hashlib.sha256(original.read_bytes()).hexdigest()==json.loads((P/'framing-study.json').read_text())['source_sha256']
q=json.loads((P/'preview-qa.json').read_text());q.update(non_camera_scene_matches_original=True,camera_height_and_lens_fixed_all_frames=True,first_last_raw_frames_identical=True,original_blend_preserved=True,camera_states=states,visual_review='Six frames extracted from the final encoded preview plus five successive crossing samples inspected. No framing or background defect. Deliberately low sample count leaves visible grain. Normal-speed playback was not directly available.')
(P/'preview-qa.json').write_text(json.dumps(q,indent=2)+'\n');print('Scene and preview preservation checks passed.')
