"""한 중심에서 뻗는 평면 사각형을 접어 빛과 그림자의 조형을 만든다."""
import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;O=P/'output';O.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials):bpy.data.materials.remove(data)
def mat(name,color,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
paper=mat('Saffron paper',(0.88,.40,.055),.74);back=mat('Warm reverse',(.68,.16,.045),.78);floor=mat('Pale blue ground',(.35,.53,.57),.85)
N=24;start=math.radians(-18);sweep=math.radians(264);inner=.72;outer=3.2;slope=.27
verts=[]
for i in range(N+1):
 a=start+sweep*i/N;k=slope if i%2 else 0
 for r in (inner,outer):verts.append((r*math.cos(a),r*math.sin(a),.04+r*k))
faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(N)]
mesh=bpy.data.meshes.new('Planar radial pleats');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Folded annular sheet',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(paper);ob.data.materials.append(back)
solid=ob.modifiers.new('Paper thickness','SOLIDIFY');solid.thickness=.018;solid.offset=0;solid.material_offset=1;solid.material_offset_rim=1
bevel=ob.modifiers.new('Small physical edges','BEVEL');bevel.width=.006;bevel.segments=2
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.name='Ground';bpy.context.object.data.materials.append(floor)
bpy.ops.object.camera_add(location=(5.7,-8.7,8.4));cam=bpy.context.object;target=Vector((0,0,.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=9.1;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-3,-4,8));light=bpy.context.object;light.name='One broad daylight source';light.data.energy=1400;light.data.shape='DISK';light.data.size=.45;light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.cycles.seed=37
scene.world.color=(.16,.16,.16);scene.view_settings.view_transform='AgX';scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False;scene.render.filepath=str(O/'Folds-of-Daylight.png')
scene['artwork_note']='평면 패널의 가상 조형. 실제 종이 물성·접힘 과정·제조 가능성을 검증하지 않음.'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Folds-of-Daylight.blend'));bpy.ops.render.render(write_still=True)
