"""Independent raycast checks of saved road and terrain meshes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(__file__).resolve().parent
terrain=bpy.data.objects['Roadbed blended meadow'];road=bpy.data.objects['Road and viewpoint apron']
def bvh(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],all_triangles=False)
t=bvh(terrain);r=bvh(road);clear=[];miss=0
for f in road.data.polygons:
 for v in [f.center]+[road.data.vertices[i].co.lerp(f.center,.1) for i in f.vertices]:
  top=Vector((v.x,v.y,100));hit=t.ray_cast(top,Vector((0,0,-1)))[0];rh=r.ray_cast(top,Vector((0,0,-1)))[0]
  if hit is None or rh is None:miss+=1
  else:clear.append(rh.z-hit.z)
report=json.loads((p/f"validation_{bpy.context.scene['seed']}.json").read_text());report.update({'terrain_non_upward_faces':sum(f.normal.z<=0 for f in terrain.data.polygons),'mesh_raycast_samples':len(clear),'mesh_raycast_misses':miss,'mesh_clearance_min_m':min(clear),'mesh_clearance_max_m':max(clear),'mesh_below_terrain_samples':sum(c<0 for c in clear)})
(p/'saved_blend_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
assert all(f.normal.z>0 for f in terrain.data.polygons) and miss==0 and min(clear)>0, 'Road intersection detected'
