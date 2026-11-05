"""접힌 파도: an original procedural virtual sculpture, not a physical prototype."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;preview='--preview' in sys.argv
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32 if preview else 160;s.cycles.use_denoising=False;s.cycles.max_bounces=6
s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=700 if preview else 1200;s.render.resolution_y=700 if preview else 1200;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='AgX'
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.74,.83,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3

def mat(name,c,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough;return m
blue=mat('Ultramarine painted paper',(.015,.075,.68),.65);back=mat('Lighter blue reverse',(.075,.19,.7),.8);orange=mat('Vermilion sphere',(.95,.105,.018),.4);ground=mat('Warm chalk background',(.82,.79,.69),.86)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025));bpy.context.object.name='Continuous ground';bpy.context.object.data.materials.append(ground)
# One continuous folded sheet. A narrow rear offset gives a restrained twist
# without subdividing the folds into smooth waves.
profile=[(-2.5,0),(-1.67,0),(-.96,1.34),(-.17,.18),(.68,2.23),(1.36,1.05),(2.36,0),(2.72,0)]
verts=[]
for i,(x,z) in enumerate(profile):
 half=.68+.06*math.sin(i*.75);cy=.13*math.sin(i*.8)
 verts.extend([(x,cy-half,z),(x,cy+half,z)])
faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(profile)-1)]
mesh=bpy.data.meshes.new('Continuous folded ribbon mesh');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Folded wave',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(blue);ob.data.materials.append(back)
sol=ob.modifiers.new('Paper thickness','SOLIDIFY');sol.thickness=.025;sol.offset=-1;sol.material_offset=1;sol.material_offset_rim=1
bevel=ob.modifiers.new('Tiny edge radius','BEVEL');bevel.width=.006;bevel.segments=2;ob.modifiers.new('Weighted face normals','WEIGHTED_NORMAL')
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.36,location=(1.56,-1.30,.335));ball=bpy.context.object;ball.name='Single vermilion sphere';ball.data.materials.append(orange)
for p in ball.data.polygons:p.use_smooth=True
# Large single source keeps the folded silhouette legible; no borrowed textures.
bpy.ops.object.light_add(type='AREA',location=(-3.8,-4.8,7.5));l=bpy.context.object;l.name='Clear daylight';l.data.energy=1450;l.data.size=1.0;l.data.color=(1,.89,.71);l.rotation_euler=(Vector((0,0,.5))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(4,2,4));l=bpy.context.object;l.name='Quiet blue fill';l.data.energy=90;l.data.size=5;l.data.color=(.66,.79,1);l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6.4,-9.0,5.8));cam=bpy.context.object;target=Vector((0,0,.77));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.4;cam.location+=(cam.location-target).normalized()*16;s.camera=cam
s['artwork']='Folded Wave: original virtual sculpture; shape is not a verified load-bearing or manufacturable structure.'
s.render.filepath='//Folded-Wave.png';bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Folded-Wave.blend'),compress=True)
s.render.filepath=str(ROOT/('preview.png' if preview else 'Folded-Wave.png'));bpy.ops.render.render(write_still=True)
p=Path(s.render.filepath);raw=p.read_bytes();out=bytearray(raw[:8]);off=8
while off<len(raw):
 n=int.from_bytes(raw[off:off+4],'big');kind=raw[off+4:off+8]
 if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out.extend(raw[off:off+n+12])
 off+=n+12
p.write_bytes(out)
(ROOT/'render_conditions.json').write_text(json.dumps({'blender':bpy.app.version_string,'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':s.cycles.samples,'preview':preview,'external_images':sum(bool(i.filepath) for i in bpy.data.images),'folded_sheet_segments':len(faces),'sphere_radius':.36,'ground_z':-.025,'sphere_lowest_z':-.025},indent=2)+'\n')
