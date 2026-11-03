"""Two bounded independent tests. Originals read only, exactly one render per case."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path(__file__).resolve().parent;E=R;case=sys.argv[sys.argv.index('--')+1]
assert case in ('dish','puddle');O=R/case;O.mkdir(exist_ok=True)
source=E/('baseline/dish.blend' if case=='dish' else 'baseline/puddle.blend');source_hash=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene

def controls():
 return {'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'samples':s.cycles.samples,'seed':s.cycles.seed,'camera_matrix':[list(v) for v in s.camera.matrix_world],'camera_type':s.camera.data.type,'lens':s.camera.data.lens,'ortho_scale':s.camera.data.ortho_scale,'view':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma],'bounces':[s.cycles.max_bounces,s.cycles.diffuse_bounces,s.cycles.glossy_bounces,s.cycles.transmission_bounces,s.cycles.transparent_max_bounces],'denoising':s.cycles.use_denoising,'adaptive':[s.cycles.use_adaptive_sampling,s.cycles.adaptive_threshold],'lights':{o.name:{'matrix':[list(v) for v in o.matrix_world],'energy':o.data.energy,'color':list(o.data.color)} for o in s.objects if o.type=='LIGHT'}}
def geometry_hashes():
 return {o.name:hashlib.sha256(json.dumps({'v':[list(v.co) for v in o.data.vertices],'p':[list(p.vertices) for p in o.data.polygons]}).encode()).hexdigest() for o in s.objects if o.type=='MESH'}
def shapes(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];fs=[tuple(t.vertices) for t in m.loop_triangles];e.to_mesh_clear();return vs,fs,BVHTree.FromPolygons(vs,fs,all_triangles=True)
def count_cross(a,af,ab,b,bf,bb):
 pairs=ab.overlap(bb);count=0
 for ai,bi in pairs:
  aa=[a[i] for i in af[ai]];bs=[b[i] for i in bf[bi]]
  for src,tgt in ((aa,bs),(bs,aa)):
   for j in range(3):
    orig=src[j];delta=src[(j+1)%3]-orig
    hit=intersect_ray_tri(tgt[0],tgt[1],tgt[2],delta,orig,True)
    if hit is not None:
     t=(hit-orig).dot(delta)/delta.length_squared
     if 1e-7<t<1-1e-7:
      count+=1
      if count==1: print('FIRST_CROSS', [1000*x for x in hit], flush=True)
 return count,len(pairs)
base_controls=controls();base_geo=geometry_hashes();report={'case':case,'original_sha256':source_hash,'controls_before':base_controls,'baseline_image':'baseline/dish.png' if case=='dish' else 'baseline/puddle.png'}
if case=='dish':
 w=bpy.data.objects['Shallow water volume'];b=bpy.data.objects['Hand-shaped ceramic dish'];original=[v.co.copy() for v in w.data.vertices];bvs,bfs,bb=shapes(b)
 original_zmin=min(p.z for p in original);original_zmax=max(p.z for p in original)
 old_profile=[(.0038,.029),(.0061,.0407),(.010,.0449),(.0102,.045)]
 def old_radius(z,t):
  if z<=old_profile[0][0]:r=old_profile[0][1]
  elif z>=old_profile[-1][0]:r=old_profile[-1][1]
  else:
   for (z0,r0),(z1,r1) in zip(old_profile,old_profile[1:]):
    if z0<=z<=z1:r=r0+(r1-r0)*(z-z0)/(z1-z0);break
  return r*(1+.009*math.sin(3*t+.2)+.004*math.sin(7*t))
 zs=[original_zmin+(original_zmax-original_zmin)*i/32 for i in range(33)]
 verts=[(0,0,original_zmin)];rings=[[0]];retreats=[];clearances=[];N=192;margin=.00025
 for z in zs:
  ring=[]
  for i in range(N):
   t=2*math.pi*i/N;direction=Vector((math.cos(t),math.sin(t),0));hit,normal,index,dist=bb.ray_cast(Vector((0,0,z)),direction,.1);assert hit is not None
   oldr=old_radius(z,t);radius=min(oldr,dist-margin);assert radius>0
   retreat=oldr-radius;retreats.append(retreat*1000);clearances.append((dist-radius)*1000)
   ring.append(len(verts));verts.append((radius*math.cos(t),radius*math.sin(t),z))
  rings.append(ring)
 rings.append([len(verts)]);verts.append((0,0,original_zmax));faces=[]
 for ra,rb in zip(rings,rings[1:]):
  for i in range(N):
   j=(i+1)%N
   if len(ra)==1:faces.append((ra[0],rb[j],rb[i]))
   elif len(rb)==1:faces.append((ra[i],ra[j],rb[0]))
   else:faces.append((ra[i],ra[j],rb[j],rb[i]))
 mats=list(w.data.materials);newmesh=bpy.data.meshes.new('Water boundary with explicit artificial air gap');newmesh.from_pydata(verts,[],faces);newmesh.update();w.data=newmesh
 for mat in mats:w.data.materials.append(mat)
 for poly in w.data.polygons:poly.use_smooth=not(poly.normal.z>.999)
 bpy.context.view_layer.update();vs,fs,wb=shapes(w);n,pairs=count_cross(vs,fs,wb,bvs,bfs,bb)
 assert n==0,'Boundary fit still crosses ceramic; do not render.'
 gap=[bb.find_nearest(p)[3]*1000 for p in vs];sidegap=[g for p,g in zip(vs,gap) if p.xy.length>.001 and p.z<original_zmax-1e-7]
 report.update({'changed_category':'Water side boundary fitted radially inward at 33 fixed-height rings; top and bottom heights and flat top shading retained.','method':'At each ring/angle, first evaluated ceramic intersection from the cavity center gives maximum radius. New radius=min(original water boundary radius, ceramic radius minus 0.25 mm).','horizontal_artificial_air_gap_mm':{'requested_min':.25,'sample_min':min(clearances),'sample_max':max(clearances)},'boundary_radial_retreat_mm':{'min':min(retreats),'max':max(retreats)},'vertex_to_ceramic_distance_mm':{'min_all':min(gap),'max_all':max(gap),'side_min':min(sidegap),'side_max':max(sidegap)},'confirmed_non_coplanar_surface_edge_crossings_after':n,'BVH_candidate_pairs_after':pairs,'intersection_scope':'All evaluated triangulated surface BVH candidate pairs checked in both edge directions; 1e-7 segment-parameter endpoint tolerance. Not exact CAD intersection proof.','air_gap_limit':'Artificial detached water boundary, not a physically correct fluid-wall contact model. Side boundary tessellation changes; surface heights, shader and lighting are fixed. The separate reopen check measures top footprint preservation.','top_z_unchanged':abs(max(v.co.z for v in w.data.vertices)-original_zmax)<1e-10,'bottom_z_unchanged':abs(min(v.co.z for v in w.data.vertices)-original_zmin)<1e-10})

else:
 backgrounds=[n for n in s.world.node_tree.nodes if n.type=='BACKGROUND'];assert len(backgrounds)==1;node=backgrounds[0];assert abs(node.inputs['Strength'].default_value-.1)<1e-6
 node.inputs['Strength'].default_value=.4;report.update({'changed_category':'World Background strength only','world_strength_before':.1,'world_strength_after':.4,'limit':'Changes ground illumination as well as visible environment reflection; not a pure reflection-contribution decomposition.'})
report['controls_after']=controls();assert report['controls_after']==base_controls
new_geo=geometry_hashes();changed=[n for n in base_geo if base_geo[n]!=new_geo[n]];assert changed==(['Shallow water volume'] if case=='dish' else [])
report['changed_meshes']=changed;report['source_unchanged_before_render']=hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report['original_path']=str(source.relative_to(E));(O/'test_validation.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.filepath=str(O/'comparison.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'Test.blend'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
