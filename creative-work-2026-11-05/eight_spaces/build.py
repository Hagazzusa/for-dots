"""Eight Spaces: original interlaced paper study, with one intentional long float."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'probe'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24 if mode=='probe' else 128;s.cycles.use_denoising=False;s.cycles.max_bounces=6
s.render.resolution_x=s.render.resolution_y=640 if mode=='probe' else 1200;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.45;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.84,.9,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.24
SPACE=.18;WIDTH=.13;AMP=.022;THICK=.007;COUNT=17;CENTER=(COUNT-1)/2;GOLD_ROW=7;LEFT=-.9;RIGHT=.54;FLOAT_HEIGHT=.20

def material(name,color,rough=.75,fiber=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;nt=m.node_tree;p=nt.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if fiber:
  tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=260;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.6
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.0015;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
cream=material('Uncoated warm paper',(.74,.69,.55),.83,True)
blue=material('Muted indigo paper',(.055,.13,.16),.79,True)
gold=material('Ochre paper with a longer span',(.68,.30,.065),.78,True)
base=material('Pale unglazed support',(.61,.59,.53),.9)
floor=material('Warm studio ground',(.78,.75,.67),.92)
strips=[]
def height(t,index,axis):
 if axis=='weft' and index==GOLD_ROW and LEFT<=t<=RIGHT:
  return AMP+FLOAT_HEIGHT*math.sin(math.pi*(t-LEFT)/(RIGHT-LEFT))**2
 return (1 if axis=='weft' else -1)*AMP*math.cos(math.pi*(t/SPACE+index))
for axis in ['warp','weft']:
 for i in range(COUNT):
  fixed=(i-CENTER)*SPACE;end=CENTER*SPACE+.14+.022*math.sin(i*2.17+(0 if axis=='warp' else .7));start=-CENTER*SPACE-.14+.022*math.sin(i*1.71)
  # Dense longitudinal mesh captures curved paper without an external texture.
  steps=240;verts=[]
  for k in range(steps+1):
   t=start+(end-start)*k/steps;z=height(t,i,axis)
   for side in [-1,1]:
    verts.append((t,fixed+side*WIDTH/2,z) if axis=='weft' else (fixed+side*WIDTH/2,t,z))
  faces=[]
  for k in range(steps):
   face=(2*k,2*k+2,2*k+3,2*k+1) if axis=='weft' else (2*k,2*k+1,2*k+3,2*k+2)
   faces.append(face)
  me=bpy.data.meshes.new(f'{axis} paper mesh {i:02d}');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(f'{axis} {i:02d}',me);bpy.context.collection.objects.link(o)
  o.data.materials.append(gold if axis=='weft' and i==GOLD_ROW else (blue if axis=='weft' else cream))
  for poly in me.polygons:poly.use_smooth=True
  solid=o.modifiers.new('Paper thickness','SOLIDIFY');solid.thickness=THICK;solid.offset=0
  bevel=o.modifiers.new('Soft cut edges','BEVEL');bevel.width=.0015;bevel.segments=2
  o.modifiers.new('Weighted paper normals','WEIGHTED_NORMAL');strips.append(o)
# Support under the lowest bends, with slight edge overhang.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.0955));ped=bpy.context.object;ped.name='Low square support';ped.dimensions=(3.10,3.10,.14);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ped.data.materials.append(base)
b=ped.modifiers.new('Rounded support edge','BEVEL');b.width=.025;b.segments=4;ped.modifiers.new('Support normals','WEIGHTED_NORMAL')
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.1655));bpy.context.object.name='Studio floor';bpy.context.object.data.materials.append(floor)
target=Vector((-.10,-.05,.02))
for name,loc,power,size,color in [('Soft window',(-3.5,-4.5,7),650,3.5,(1,.88,.70)),('Quiet fill',(4,2,5),120,4,(.73,.86,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.size=size;l.data.color=color;l.rotation_euler=(target-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4.8,-5.8,6.8));cam=bpy.context.object;cam.name='Paper study camera';cam.data.type='ORTHO';cam.data.ortho_scale=5.3;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
# Check evaluated strip surfaces, including thickness and bevel, for overlap.
trees={o.name:BVHTree.FromObject(o,deps) for o in strips};overlaps=[]
for a in strips:
 if not a.name.startswith('warp'):continue
 for b in strips:
  if not b.name.startswith('weft'):continue
  pairs=trees[a.name].overlap(trees[b.name])
  if pairs:overlaps.append({'a':a.name,'b':b.name,'face_pairs':len(pairs)})
assert not overlaps,overlaps
margin=1
for o in strips+[ped]:
 ev=o.evaluated_get(deps)
 for corner in ev.bound_box:
  v=world_to_camera_view(s,cam,ev.matrix_world@Vector(corner));margin=min(margin,v.x,1-v.x,v.y,1-v.y)
assert margin>.055,margin
endpoint_errors=[]
for t in [LEFT,RIGHT]:
 value_error=abs(height(t,GOLD_ROW,'weft')-AMP*math.cos(math.pi*(t/SPACE+GOLD_ROW)))
 slope_error=abs(-AMP*math.pi/SPACE*math.sin(math.pi*(t/SPACE+GOLD_ROW)))
 assert value_error<1e-10 and slope_error<1e-10
 endpoint_errors.append({'position':t,'value_error':value_error,'slope_error':slope_error})
assert abs((RIGHT-LEFT)/SPACE-8)<1e-10
records=[]
for i in range(COUNT):
 for j in range(COUNT):
  zw=height((i-CENTER)*SPACE,j,'weft');zv=height((j-CENTER)*SPACE,i,'warp')
  records.append({'warp':i,'weft':j,'weft_minus_warp_height':round(zw-zv,6)})
q={'minimum_conservative_frame_margin':margin,'strip_count':len(strips),'crossings':COUNT**2,'grid_pitch':SPACE,'strip_width':WIDTH,'thickness':THICK,'regular_weave_amplitude':AMP,'long_float_row':GOLD_ROW,'long_float_interval':[LEFT,RIGHT],'long_float_grid_intervals':(RIGHT-LEFT)/SPACE,'long_float_extra_height':FLOAT_HEIGHT,'analytic_endpoint_continuity_errors':endpoint_errors,'minimum_crossing_center_clearance_after_nominal_thickness':min(abs(r['weft_minus_warp_height'])-THICK for r in records),'evaluated_mesh_overlap_pairs':overlaps,'check_scope':'BVH surface-overlap check between every warp/weft pair, and crossing-center height checks. No material mechanics or stress simulation.','crossing_records':records}
(P/'geometry-check.json').write_text(json.dumps(q,indent=2)+'\n')
s.render.filepath='//Eight-Spaces.png';bpy.ops.wm.save_as_mainfile(filepath=str(P/'Eight-Spaces.blend'),compress=True)
(P/'build-config.json').write_text(json.dumps({'mode':mode,'resolution':s.render.resolution_x,'samples':s.cycles.samples,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('Built and verified',mode)
