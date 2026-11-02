"""Original FreeCAD mesh preview, Blender 4.3; serial CPU render."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in json.loads((P/'preview_mesh.json').read_text()):
 mesh=bpy.data.meshes.new(d['name']);mesh.from_pydata([[x/100 for x in v] for v in d['vertices']],[],d['faces']);mesh.update();o=bpy.data.objects.new(d['name'],mesh);bpy.context.collection.objects.link(o)
 m=bpy.data.materials.new(d['name']);m.diffuse_color=(*d['color'],1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*d['color'],1);p.inputs['Metallic'].default_value=.5 if 'track' in d['name'] or 'axle' in d['name'] else .15;p.inputs['Roughness'].default_value=.4;o.data.materials.append(m)
 if 'pane' in d['name']:p.inputs['Emission Color'].default_value=(*d['color'],1);p.inputs['Emission Strength'].default_value=.7
 for poly in mesh.polygons:poly.use_smooth=False
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.location.z=-.03
m=bpy.data.materials.new('Ground');m.diffuse_color=(.12,.16,.18,1);bpy.context.object.data.materials.append(m)
def light(loc,energy,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
light((0,-5,7),900,5);light((5,3,6),1100,4)
bpy.ops.object.camera_add(location=(5,-10,5.3));c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=5.3
sc=bpy.context.scene;sc.camera=c;sc.world.color=(.18,.18,.18);sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=900;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX'
for label,loc,target in [('quarter',(5,-10,5.3),(0,0,1.9)),('front',(0,-10,1.9),(0,0,1.9))]:
 c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/('rear_axle_'+label+'.png'));bpy.ops.render.render(write_still=True)
