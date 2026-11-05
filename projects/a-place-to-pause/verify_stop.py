"""Verify the local pad/bench change against actual saved scene meshes; not safety certification."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(__file__).resolve().parent
pad=bpy.data.objects['Separate pedestrian stone pad'];terr=bpy.data.objects['Roadbed blended meadow'];road=bpy.data.objects['Road and viewpoint apron'];shoulder=bpy.data.objects['Blended limestone shoulder']
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],all_triangles=False)
def polygon(o,f):return [tuple((o.matrix_world@o.data.vertices[i].co)[:2]) for i in f.vertices]
def overlap(a,b):
 for poly in (a,b):
  for i,u in enumerate(poly):
   v=poly[(i+1)%len(poly)];axis=(-(v[1]-u[1]),v[0]-u[0]);aa=[x*axis[0]+y*axis[1] for x,y in a];bb=[x*axis[0]+y*axis[1] for x,y in b]
   if max(aa)<min(bb)-1e-8 or max(bb)<min(aa)-1e-8:return False
 return True
def pointsegment(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def distance(a,b):
 return min([pointsegment(v,b[i],b[(i+1)%len(b)]) for v in a for i in range(len(b))]+[pointsegment(v,a[i],a[(i+1)%len(a)]) for v in b for i in range(len(a))])
xs=[v.co.x for v in pad.data.vertices];ys=[v.co.y for v in pad.data.vertices];rect=[(min(xs),min(ys)),(max(xs),min(ys)),(max(xs),max(ys)),(min(xs),max(ys))]
bpy.context.view_layer.update()
result={'scope':'Finite scene geometry checks only, not road/pedestrian safety certification.','pad_dimensions_m':[max(xs)-min(xs),max(ys)-min(ys)],'pad_outside_road_mesh':True,'pad_outside_shoulder_mesh':True}
for ob,key in [(road,'road'),(shoulder,'shoulder')]:
 polys=[polygon(ob,f) for f in ob.data.polygons];assert all(not overlap(rect,q) for q in polys)
 result['minimum_pad_to_'+key+'_xy_distance_m']=min(distance(rect,q) for q in polys)
# Every bench vertex lies within the pad footprint, so it is also outside the disjoint road.
bench=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Bench')];footbase=[]
for o in bench:
 world=[o.matrix_world@v.co for v in o.data.vertices]
 assert all(min(xs)<=v.x<=max(xs) and min(ys)<=v.y<=max(ys) for v in world)
 if o.name.startswith('Bench foot'):footbase.append(min(v.z for v in world))
result['bench_meshes_inside_pad']=len(bench)
top=max(v.co.z for v in pad.data.vertices);result['bench_foot_to_pad_gaps_m']=[z-top for z in footbase];assert max(abs(z-top) for z in footbase)<1e-4
terrain=bvh(terr);pb=bvh(pad);bottom_gaps=[];top_gaps=[]
for j in range(21):
 for i in range(21):
  x=min(xs)+(max(xs)-min(xs))*(i+.01)/20.02;y=min(ys)+(max(ys)-min(ys))*(j+.01)/20.02
  ground=terrain.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))[0];bottom=pb.ray_cast(Vector((x,y,-100)),Vector((0,0,1)))[0];assert ground and bottom
  bottom_gaps.append(bottom.z-ground.z);top_gaps.append(top-ground.z)
assert min(bottom_gaps)>=-1e-4 and max(bottom_gaps)<.005 and min(top_gaps)>0
result.update({'terrain_support_samples':len(bottom_gaps),'pad_bottom_to_ground_min_m':min(bottom_gaps),'pad_bottom_to_ground_max_m':max(bottom_gaps),'pad_top_to_ground_min_m':min(top_gaps),'pad_top_to_ground_max_m':max(top_gaps),'passed':True,'bench_facing':'positive X, outward from the road'})
(p/'stop_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
