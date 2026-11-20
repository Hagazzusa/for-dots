"""Blender 저장 장면의 실제 광선과 눈 위치를 독립 검사한다."""
import bpy,json
from mathutils import Vector
from pathlib import Path
root=Path(bpy.data.filepath).parent
spec=json.loads((root/'model.json').read_text())
points=[('body',(50,79.92,46)),('toe',(38,79.92,41)),('heel',(61,79.82,38)),('clamp',(66,79.80,42))]
results=[]
for side,eye in spec['eyes'].items():
 cam=bpy.data.objects['view_'+side]
 assert (cam.location-Vector(eye)*.001).length<1e-8
 for name,p in points:
  origin=Vector(eye)*.001;target=Vector(p)*.001;direction=(target-origin).normalized()
  hit,loc,normal,index,obj,matrix=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=(target-origin).length+.002)
  assert hit
  if side=='left':assert obj.name.startswith(('cabinet','drawer')),obj.name
  else:assert obj.name.startswith(('repair_','fresh_','clamp_')),obj.name
  results.append({'view':side,'point':name,'hit':obj.name})
assert not [im for im in bpy.data.images if im.source=='FILE']
print(json.dumps({'native_ray_tests':results,'external_images':0},ensure_ascii=False,indent=2))
