"""Rain Clock — original procedural virtual sculpture. Blender 4.3+.
Run: blender -b -t 2 --python build.py [-- --still | --loop]
No flag builds and saves only. Stylized animation, not mechanical simulation.
"""
import bpy, math, os, sys
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials): bpy.data.materials.remove(x)
def mat(name, color, metal=0, rough=.4, emission=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 if emission: p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
 return m
ink=mat('Midnight enamel',(.025,.065,.075),.35,.28)
brass=mat('Satin champagne brass',(.56,.34,.13),.72,.3)
blue=mat('Rain / celadon ceramic',(.11,.48,.49),.18,.22)
warm=mat('Window / amber porcelain',(.95,.42,.12),0,.4,2.3)
black=mat('Window recess',(.009,.025,.028),0,.7)
stone=mat('Graphite terrazzo',(.07,.085,.09),0,.72)
floor=mat('Studio ground',(.13,.17,.18),0,.85)
def finish(o,name,m):
 o.name=name; o.data.materials.append(m); return o
def box(name,loc,scale,m,bevel=.05):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=finish(bpy.context.object,name,m); o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel: mod=o.modifiers.new('Soft machined edges','BEVEL'); mod.width=bevel; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def rod(name,a,b,r,m):
 d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=finish(bpy.context.object,name,m); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o
def arc(name,r,y,z,m,thick=.025):
 c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=thick; c.bevel_resolution=3
 s=c.splines.new('POLY'); s.points.add(127)
 for i,p in enumerate(s.points):
  a=2*math.pi*i/128; p.co=(r*math.cos(a),0,r*math.sin(a),1)
 s.use_cyclic_u=True; o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.location=(0,y,z); c.materials.append(m); return o
box('Low oval-edged plinth',(0,0,.2),(3.9,1.25,.4),stone,.17)
box('Floating enamel deck',(0,0,.43),(3.6,1.04,.12),ink,.06)
for x in [-1.62,1.62]: rod('Support stem',(x,.18,.49),(x,.18,2.1),.045,brass)
arc('Stationary perimeter',1.62,.18,2.1,ink,.075)
# A small warm refuge held inside the field of rain.
box('Recessed window casing',(0,.23,1.45),(1.12,.29,1.35),ink,.09)
box('Black reveal',(0,.065,1.45),(.94,.05,1.17),black,.04)
box('Warm pane',(0,.025,1.45),(.78,.045,1.02),warm,.02)
box('Vertical mullion',(0,-.012,1.45),(.035,.07,1.04),brass,.007)
box('Horizontal mullion',(0,-.012,1.45),(.8,.07,.035),brass,.007)
box('Overhanging shelter canopy',(0,.04,2.17),(1.34,.72,.09),brass,.025)
box('Window sill',(0,-.03,.88),(1.3,.55,.08),brass,.02)
# Two almost concentric rain paths, offset in depth and out of phase.
for j,(r,y) in enumerate([(1.39,-.02),(1.12,-.19)]):
 pivot=bpy.data.objects.new('Rain rhythm %d / editable motion'%(j+1),None); bpy.context.collection.objects.link(pivot); pivot.location=(0,y,2.1)
 o=arc('Fine orbit %d'%j,r,y,2.1,brass,.014); o.parent=pivot; o.matrix_parent_inverse=pivot.matrix_world.inverted()
 # Set local transforms explicitly to avoid dependency graph ambiguity.
 o.matrix_parent_inverse.identity(); o.location=(0,0,0)
 for k in range(11 if j==0 else 8):
  a=(k/(11 if j==0 else 8))*math.tau+.2*j
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1)
  bead=finish(bpy.context.object,'Rain bead %d.%02d'%(j,k),blue if k%3 else brass); bead.parent=pivot; bead.location=(r*math.cos(a),0,r*math.sin(a)); bead.scale=(.058,.046,.105)
  for poly in bead.data.polygons: poly.use_smooth=True
 for f in range(1,98):
  t=(f-1)/96*math.tau; pivot.rotation_euler[1]=(.15 if j==0 else -.19)*math.sin(t+j*math.pi/2); pivot.keyframe_insert(data_path='rotation_euler',index=1,frame=f)
 if pivot.animation_data:
  for fc in pivot.animation_data.action.fcurves:
   for kp in fc.keyframe_points: kp.interpolation='LINEAR'
# Decorative fixed drip ticks on the top rim: deliberate asymmetry.
for i in range(5):
 x=-.35+i*.175; z=2.1+math.sqrt(1.62**2-x*x); rod('Crown rain tick',(x,.18,z-.03),(x,.18,z+.06),.013,brass)
box('Small nameplate',(0,-.641,.205),(1.18,.018,.16),brass,.018)
bpy.ops.object.text_add(location=(0,-.655,.17),rotation=(math.pi/2,0,0)); txt=bpy.context.object; txt.name='RAIN CLOCK / engraved label'; txt.data.body='R A I N   C L O C K'; txt.data.align_x='CENTER'; txt.data.size=.073; txt.data.extrude=.0005; txt.data.materials.append(ink)
box('Studio sweep',(0,0,-.1),(200,200,.1),floor,.0)
def area(name,loc,power,color,size,target=(0,0,1.8)):
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Softbox / cool sky',(-3,-4,7),600,(.7,.87,1),5)
area('Warm rim',(3,2,5),750,(1,.72,.42),3)
area('Front fill',(1,-4,2.5),100,(.75,1,1),3)
bpy.ops.object.camera_add(location=(5,-10,5.3)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.9))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.2
sc=bpy.context.scene; sc.camera=cam; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=False; sc.render.threads_mode='FIXED'; sc.render.threads=2
sc.world.color=(.18,.18,.18); sc.render.resolution_x=800; sc.render.resolution_y=800; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.fps=12; sc.frame_start=1; sc.frame_end=96; sc.frame_set(1)
sc.view_settings.view_transform='AgX'; sc['study']='Virtual kinetic design study only; no engineering, timekeeping, or manufacturability claim.'
sc.render.filepath='//renders/'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'rain_clock.blend'))
if '--still' in sys.argv:
 sc.render.filepath=os.path.join(ROOT,'rain_clock_still.png'); bpy.ops.render.render(write_still=True)
if '--loop' in sys.argv:
 sc.render.resolution_x=480; sc.render.resolution_y=480; sc.cycles.samples=8
 os.makedirs(os.path.join(ROOT,'frames'),exist_ok=True)
 for f in range(1,97,2):
  sc.frame_set(f); sc.render.filepath=os.path.join(ROOT,'frames',f'{f:04d}.png'); bpy.ops.render.render(write_still=True)
print('RAIN_CLOCK_OK',len(bpy.data.objects),'objects')
