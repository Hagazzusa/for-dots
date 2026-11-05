import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'One-View-Circle.blend'));s=bpy.context.scene;cam=s.camera
arcs=[o for o in s.objects if o.name.startswith('Arc ')];assert len(arcs)==8
s.frame_set(1);first=[list(row) for o in arcs for row in o.matrix_world]
cameras=[]
for f in [1,24,48,72,96]:
 s.frame_set(f);cameras.append({'frame':f,'location':list(cam.location),'lens':cam.data.lens})
assert first==[list(row) for o in arcs for row in o.matrix_world]
assert all(o.animation_data is None for o in arcs)
out={'objects':len(s.objects),'arc_count':len(arcs),'arc_transforms_static':True,'camera_type':cam.data.type,'camera_states':cameras,'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':s.cycles.samples,'external_images':sum(bool(i.filepath) for i in bpy.data.images),'render_path':s.render.filepath}
(root/'readback.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
