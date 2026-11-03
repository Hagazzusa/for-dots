"""Reopen final native scene read-only and record bounded checks."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'Returned_Cart.blend'));dg=bpy.context.evaluated_depsgraph_get();s=bpy.context.scene
finite=True;zero=0;meshes=0;vertices=0
for o in s.objects:
 if o.type=='MESH':
  e=o.evaluated_get(dg);m=e.to_mesh();meshes+=1;vertices+=len(m.vertices)
  finite &= all(math.isfinite(c) for v in m.vertices for c in v.co);zero+=sum(p.area<1e-14 for p in m.polygons);e.to_mesh_clear()
assert finite and zero==0
assert s.render.filepath=='//renders/returned_cart_final.png'
paths=[]
for o in list(bpy.data.images)+list(bpy.data.libraries)+list(bpy.data.fonts)+list(bpy.data.sounds)+list(bpy.data.movieclips):
 p=getattr(o,'filepath','')
 if p and p!='<builtin>' and not p.startswith('//'):paths.append({'name':o.name,'absolute_or_external':True})
assert not paths,paths
raw=(R/'Returned_Cart.blend').read_bytes();private_tokens={p.decode():raw.count(p) for p in (b'/workspace/',b'/home/',b'/tmp/')};assert not any(private_tokens.values()),private_tokens
wheel_samples=[];receivers=[]
for ob in s.objects:
 if ob.name.startswith('Individual paving slab') or ob.name=='Paving foundation':
  e=ob.evaluated_get(dg);m=e.to_mesh();receivers.append((ob.name,BVHTree.FromPolygons([ob.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons])));e.to_mesh_clear()
for o in s.objects:
 if o.name=='Wheel' or o.name.startswith('Wheel.'):
  bounds=[o.matrix_world@Vector(x) for x in o.bound_box];z=min(v.z for v in bounds);x=o.location.x;y=o.location.y;hits=[]
  for name,bvh in receivers:
   point,normal,index,distance=bvh.ray_cast(Vector((x,y,.3)),Vector((0,0,-1)),.5)
   if point is not None:hits.append((point.z,name))
  top,name=max(hits)
  wheel_samples.append({'name':o.name,'bottom_z_mm':z*1000,'underlying_center_surface':name,'center_ray_gap_mm':(z-top)*1000,'interpretation':'Centerline-only sample; a center over a grout gap is not whole-tire separation. Adjacent footprint not exhaustively tested.'})
strap=bpy.data.objects['Open asymmetric canvas strap'];assert len(strap.data.vertices)>100
r={'native_reopened':True,'finite_evaluated_vertices':finite,'zero_area_faces':zero,'evaluated_meshes':meshes,'evaluated_vertices':vertices,'external_file_references':paths,'private_absolute_path_token_counts':private_tokens,'relative_render_path':s.render.filepath,'wheel_bottom_ray_samples':wheel_samples,'nominal_rear_wheel_step_clearance_mm':128.5,'strap':'One manually modeled open ribbon mesh; no cloth simulation. Tiny contact offsets not globally certified.','render':{'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':s.cycles.samples,'engine':'Cycles CPU','threads':s.render.threads,'denoising':s.cycles.use_denoising},'limits':'Finite sampled geometry checks, not an exhaustive collision proof, mechanical design, tire deformation, transport load or safety validation.'}
(R/'native_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
