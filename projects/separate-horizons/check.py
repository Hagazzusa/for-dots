"""Read back the saved sculpture; inspect closed meshes, volume, surfaces and framing."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'Separate-Horizons.blend'));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();report={'meshes':{},'water_vessel_overlap':{},'all_water_surface_heights':[]}
for o in s.objects:
 if o.type!='MESH' or o.name=='Ground':continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True)
 assert bad==0,(o.name,bad)
 assert vol>0,(o.name,vol)
 report['meshes'][o.name]={'vertices':len(bm.verts),'nonmanifold_edges':bad,'signed_volume':vol};bm.free()
 if o.name.startswith('Water '):
  top=max(o.data.polygons,key=lambda f:f.normal.z);heights=[o.data.vertices[i].co.z for i in top.vertices]
  assert len(heights)==192 and max(heights)-min(heights)<1e-6
  assert top.normal.z>.999999
  report['all_water_surface_heights'].append(sum(heights)/len(heights))
  vessel=bpy.data.objects[o.name.replace('Water ','Vessel ')]
  overlaps=BVHTree.FromObject(o,deps).overlap(BVHTree.FromObject(vessel,deps));report['water_vessel_overlap'][o.name]=len(overlaps);assert not overlaps,(o.name,len(overlaps))
vessels=[o for o in s.objects if o.name.startswith('Vessel ')]
report['vessel_pair_overlap']=len(BVHTree.FromObject(vessels[0],deps).overlap(BVHTree.FromObject(vessels[1],deps)))
assert report['vessel_pair_overlap']==0
report['support_seating']={}
for o in s.objects:
 if not o.name.startswith('Inclined support '):continue
 top=max((p for p in o.data.polygons if len(p.vertices)>100),key=lambda p:p.normal.z)
 points=[o.data.vertices[i].co for i in top.vertices];center=sum(points,Vector())/len(points)
 max_radius=max((v-center).length for v in points);assert max_radius<.72
 vessel=bpy.data.objects[o.name.replace('Inclined support ','Vessel ')]
 d=[abs((v.co-center).dot(top.normal)) for v in vessel.data.vertices]
 contacts=sum(x<1e-6 for x in d);assert contacts>=192
 report['support_seating'][o.name]={'top_radius_in_inclined_plane':max_radius,'vessel_base_radius':.72,'coplanar_vessel_base_vertices':contacts}
coords=[world_to_camera_view(s,s.camera,o.matrix_world@v.co) for o in s.objects if o.type=='MESH' and o.name!='Ground' for v in o.data.vertices]
report['frame_min_margin']=min(min(v.x,1-v.x,v.y,1-v.y) for v in coords);assert report['frame_min_margin']>.08
report['surface_height_range']=max(report['all_water_surface_heights'])-min(report['all_water_surface_heights']);assert report['surface_height_range']<1e-6
report['render']={'width':s.render.resolution_x,'height':s.render.resolution_y,'samples':s.cycles.samples,'denoising':s.cycles.use_denoising}
(P/'readback-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
