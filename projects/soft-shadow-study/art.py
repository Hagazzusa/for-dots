"""Three heights, one light. Original procedural virtual sculpture."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=False; s.cycles.transparent_max_bounces=12
s.render.threads_mode='FIXED'; s.render.threads=2; s.render.resolution_x=800; s.render.resolution_y=700; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.view_settings.view_transform='AgX'; s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.7,.8,1,1); s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.1

def mat(name,col,rough=.8,metal=0):
 m=bpy.data.materials.new(name); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m
paper=mat('Ivory paper',(.75,.72,.63),.95); ground=mat('Warm grey',(.26,.27,.26)); metal=mat('Quiet satin brass',(.38,.3,.19),.4,.65)
n=paper.node_tree.nodes; l=paper.node_tree.links; noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=170; bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.01; l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],n.get('Principled BSDF').inputs['Normal'])
f=bpy.data.materials.new('Mist teal thin filter / no refraction'); f.use_nodes=True; n=f.node_tree.nodes; n.clear(); l=f.node_tree.links; t=n.new('ShaderNodeBsdfTransparent'); t.inputs['Color'].default_value=(.23,.78,.68,1); d=n.new('ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value=(.23,.78,.68,1); mix=n.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.08; l.new(t.outputs[0],mix.inputs[1]); l.new(d.outputs[0],mix.inputs[2]); out=n.new('ShaderNodeOutputMaterial'); l.new(mix.outputs[0],out.inputs[0])
def cube(name,loc,scale,ma,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); ob.data.materials.append(ma); mod=ob.modifiers.new('Soft edge','BEVEL'); mod.width=bevel; mod.segments=4; ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return ob
cube('Paper plinth',(0,.5,-.13),(7.5,5.5,.24),paper,.12); cube('Studio',(0,0,-.31),(200,200,.1),ground,.02)
for i,(x,gap) in enumerate([(-2,.4),(0,.9),(2,1.4)]):
 # The same rounded filter at three distances from the receiver.
 pts=[]; w=.95; h=1.1; r=.12
 for cx,cy,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(9):
   theta=math.radians(a+j*90/8); pts.append((cx+r*math.cos(theta),cy+r*math.sin(theta),0))
 mesh=bpy.data.meshes.new(f'Filter {i+1}'); mesh.from_pydata(pts,[],[list(range(len(pts)))]); mesh.update(); ob=bpy.data.objects.new(f'{i+1} / gap {gap}',mesh); bpy.context.collection.objects.link(ob); ob.location=(x,-.65,gap); ob.data.materials.append(f)
 curve=bpy.data.curves.new('Fine rounded rim','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.011; curve.bevel_resolution=3; sp=curve.splines.new('POLY'); sp.points.add(len(pts)-1)
 for q,co in zip(sp.points,pts): q.co=(*co,1)
 sp.use_cyclic_u=True; rim=bpy.data.objects.new('Champagne outline',curve); bpy.context.collection.objects.link(rim); rim.location=ob.location; rim.data.materials.append(metal)
 for dx in [-.37,.37]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.014,depth=gap,location=(x+dx,-1.08,gap/2)); bpy.context.object.name='Slender support'; bpy.context.object.data.materials.append(metal)
 cube('Small foot',(x,-1.08,.025),(.9,.19,.05),paper,.02)
 # Small neutral specimen marks, not a chart within the artwork.
 for mark in range(i+1): cube('Index mark',(x-.04*i+.08*mark,-1.48,.003),(.022,.085,.006),metal,.003)
bpy.ops.object.light_add(type='AREA',location=(-2.8,-4.5,6.5)); light=bpy.context.object; light.name='One broad afternoon emitter'; light.data.energy=1700; light.data.size=1.2; light.data.shape='SQUARE'; light.data.color=(1,.93,.83); light.rotation_euler=(Vector((0,.2,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-8,8)); camera=bpy.context.object; camera.name='Quiet gallery view'; camera.rotation_euler=(Vector((0,.4,.1))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=10.6; s.camera=camera
s['description']='Three heights, one light. Virtual thin non-refracting teal filters, increasingly soft colored shadow boundaries. Artistic illustration, not a calibrated measurement scene.'
s.render.filepath='//Three-Heights-One-Light.png'; bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Three-Heights-One-Light.blend')); s.render.filepath=str(ROOT/'Three-Heights-One-Light.png'); bpy.ops.render.render(write_still=True)
