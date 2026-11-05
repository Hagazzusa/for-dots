"""Original procedural virtual light study. Run with Blender 4.3+; see README."""
import bpy, math, argparse, sys, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser(); p.add_argument('--render',choices=['still','loop','none'],default='still'); opts=p.parse_args(args)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.render.threads_mode='FIXED'; s.render.threads=2
s.cycles.samples=64; s.cycles.use_denoising=False; s.cycles.max_bounces=8; s.cycles.transparent_max_bounces=12
s.render.resolution_x=800; s.render.resolution_y=800; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.view_settings.view_transform='AgX'; s.world.color=(.12,.12,.12)
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.73,.8,1,1); s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.13
s.render.fps=12; s.frame_start=1; s.frame_end=48

def mat(name,col,rough=.6,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m
paper=mat('Warm cotton paper',(.72,.69,.61),.92)
n=paper.node_tree.nodes; l=paper.node_tree.links; noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=180; noise.inputs['Detail'].default_value=2; bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.012; l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
base=mat('Ivory ceramic',(.74,.72,.65),.4); brass=mat('Satin champagne metal',(.4,.29,.15),.35,.7); backdrop=mat('Warm grey background',(.25,.26,.25),.95)
def cube(name,loc,scale,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); ob.data.materials.append(ma)
 if bevel: mod=ob.modifiers.new('Soft handmade edges','BEVEL'); mod.width=bevel; mod.segments=4; ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return ob
cube('Paper display slab',(0,.5,-.13),(7,6,.24),paper,.13)
cube('Studio ground',(0,0,-.31),(200,200,.1),backdrop)
# Thin-sheet BSDF approximation: colored transmission without refraction or caustic focusing.
def filtermat(name,col):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True; n=m.node_tree.nodes; n.clear(); l=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial'); trans=n.new('ShaderNodeBsdfTransparent'); trans.inputs['Color'].default_value=(*col,1)
 diffuse=n.new('ShaderNodeBsdfDiffuse'); diffuse.inputs['Color'].default_value=(*col,1); diffuse.inputs['Roughness'].default_value=.3
 mix=n.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.12; l.new(trans.outputs[0],mix.inputs[1]); l.new(diffuse.outputs[0],mix.inputs[2]); l.new(mix.outputs[0],out.inputs['Surface']); return m
# Rounded-rectangle planar filters; all curves are generated, no external assets.
def panel(name,x,y,w,h,col,angle):
 r=.19; pts=[]
 for cx,cz,a in [(w/2-r,h-r,0),(-w/2+r,h-r,90),(-w/2+r,r,180),(w/2-r,r,270)]:
  for j in range(9):
   t=math.radians(a+j*90/8); pts.append((cx+r*math.cos(t),0,cz+r*math.sin(t)))
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(pts,[],[list(range(len(pts)))]); mesh.update(); ob=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(ob); ob.location=(x,y,.13); ob.rotation_euler[2]=angle; ob.data.materials.append(filtermat(name+' / thin optical filter',col))
 # Thin metal outline gives the physically thin surface a visible edge.
 curve=bpy.data.curves.new(name+' perimeter','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.012; curve.bevel_resolution=3; spline=curve.splines.new('POLY'); spline.points.add(len(pts)-1)
 for q,co in zip(spline.points,pts): q.co=(*co,1)
 spline.use_cyclic_u=True; rim=bpy.data.objects.new(name+' champagne rim',curve); bpy.context.collection.objects.link(rim); rim.location=ob.location; rim.rotation_euler=ob.rotation_euler; rim.data.materials.append(brass)
 foot=cube(name+' ceramic foot',(x,y,.055),(w*.65,.38,.12),base,.045); foot.rotation_euler[2]=angle
 return ob
panel('01 Apricot',-1.5,-.2,1.28,2.05,(1,.46,.21),-.12)
panel('02 Mist teal',0,.38,1.12,2.65,(.27,.86,.78),.08)
panel('03 Dusty violet',1.45,.02,1.28,1.8,(.64,.39,.88),-.18)
bpy.ops.object.light_add(type='AREA',location=(-3,-4,6)); light=bpy.context.object; light.name='Slow circular afternoon'; light.data.energy=1400; light.data.shape='DISK'; light.data.size=.65; light.data.color=(1,.91,.78)
def pose(frame):
 t=2*math.pi*(frame-1)/48
 light.location=(-3+.75*math.cos(t),-4+.55*math.sin(t),6+.3*math.sin(t))
 light.rotation_euler=(Vector((0,.4,0))-light.location).to_track_quat('-Z','Y').to_euler()
for f in range(1,50):
 pose(f); light.keyframe_insert('location',frame=f); light.keyframe_insert('rotation_euler',frame=f)
for fc in light.animation_data.action.fcurves:
 for k in fc.keyframe_points: k.interpolation='LINEAR'
 mod=fc.modifiers.new('CYCLES')
bpy.ops.object.camera_add(location=(7,-9,8)); cam=bpy.context.object; cam.name='Gallery view'; cam.rotation_euler=(Vector((0,.55,.25))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10.5; s.camera=cam
s.frame_set(1); s.render.filepath=str(ROOT/'Garden-of-Light.png')
s['description']='Garden of Light / 빛의 정원. Original virtual desk-scale installation. Thin colored non-refractive filters; no physical fabrication or caustic accuracy claim.'
s['loop']='48 frames at 12 fps; frame 49 equals frame 1; do not encode duplicate endpoint.'
s.render.filepath='//Garden-of-Light.png'  # Portable editable scene output
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Garden-of-Light.blend'))
s.render.filepath=str(ROOT/'Garden-of-Light.png')
if opts.render=='still': bpy.ops.render.render(write_still=True)
elif opts.render=='loop':
 s.render.resolution_x=s.render.resolution_y=480; s.cycles.samples=24; (ROOT/'frames').mkdir(exist_ok=True); s.render.filepath=str(ROOT/'frames'/'frame_'); bpy.ops.render.render(animation=True)
# Numerical animation closure and portable scene validation.
s.frame_set(1); start=list(light.location)+list(light.rotation_euler); s.frame_set(49); end=list(light.location)+list(light.rotation_euler)
report={'blender':bpy.app.version_string,'engine':s.render.engine,'threads':s.render.threads,'objects':len(s.objects),'loop_endpoint_max_error':max(abs(a-b) for a,b in zip(start,end)),'render_mode':opts.render}
(ROOT/('validation_'+opts.render+'.json')).write_text(json.dumps(report,indent=2)); print('GARDEN_VALIDATION',report)
