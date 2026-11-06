"""두 빗살의 어긋남: 외부 에셋 없는 편집 가능한 조형 구성."""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
def material(name,color,roughness=.3):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=roughness
 return m
blue=material('깊은 군청 · 유약',(.018,.06,.18),.25)
red=material('다홍 · 무광 수지',(.75,.075,.026),.32)
floor=material('분홍 회백색 바닥',(.57,.45,.41),.8)
def block(name,loc,size,mat,bevel=.09):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat); mod=o.modifiers.new('둥근 모서리','BEVEL'); mod.width=bevel; mod.segments=5
 mod=o.modifiers.new('면 법선','WEIGHTED_NORMAL'); return o
# 두 줄은 같은 높이의 바닥 위에 놓인다. 이빨은 x 위치를 번갈아 점유한다.
# 간격 0.50, 폭 0.38이므로 서로 다른 색 사이에 0.12의 틈이 남는다.
block('군청 등뼈',(-.25,-1.22,.32),(4.4,.42,.64),blue)
block('다홍 등뼈',(.25,1.22,.32),(4.4,.42,.64),red)
for i in range(5):
 x=-2.0+i
 block('군청 이빨 %d'%i,(x,-.13,.32),(.38,2.2,.64),blue)
for i in range(4):
 x=-1.5+i
 if i==2: continue
 block('다홍 이빨 %d'%i,(x,.13,.32),(.38,2.2,.64),red)
# 빠진 이빨은 장면 밖으로 버리지 않고 오른쪽 앞에 눕힌다.
t=block('따로 놓인 다홍 이빨',(3.3,-1.6,.32),(2.2,.38,.64),red)
t.rotation_euler[2]=math.radians(-24)
# 겹친 상자 면을 그대로 남기면 이음부에 검은 렌더 오류가 생기므로 실제 합집합한다.
def union_comb(prefix,name):
 parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefix)]
 base=next(o for o in parts if '등뼈' in o.name)
 for o in parts:
  for m in list(o.modifiers): o.modifiers.remove(m)
 bpy.context.view_layer.objects.active=base
 for o in parts:
  if o==base: continue
  mod=base.modifiers.new('실체 합집합','BOOLEAN'); mod.operation='UNION'; mod.solver='EXACT'; mod.object=o
  bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(o,do_unlink=True)
 base.name=name
 mod=base.modifiers.new('둥근 모서리','BEVEL'); mod.width=.09; mod.segments=5
 base.modifiers.new('면 법선','WEIGHTED_NORMAL')
union_comb('군청','군청 빗살')
union_comb('다홍','다홍 빗살')
block('바닥',(0,0,-.12),(200,200,.24),floor,.02)
world=bpy.data.worlds.new('연한 주변광'); bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.68,.85,1); world.node_tree.nodes['Background'].inputs[1].default_value=.3
ld=bpy.data.lights.new('큰 창','AREA'); lo=bpy.data.objects.new('큰 창',ld); bpy.context.collection.objects.link(lo); lo.location=(-3,-4,7); ld.energy=1100; ld.size=4
bpy.ops.object.camera_add(location=(7,-9,10)); cam=bpy.context.object; cam.name='감상 카메라'; cam.rotation_euler=(Vector((.65,0,0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=8.6
s=bpy.context.scene; s.camera=cam; s.render.engine='CYCLES'; s.cycles.samples=192; s.cycles.use_denoising=False; s.cycles.seed=17
s.render.resolution_x=1600; s.render.resolution_y=1400; s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'; s.render.image_settings.file_format='PNG'
s.render.filepath=os.path.join(ROOT,'output','One-Tooth-Apart.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'output','One-Tooth-Apart.blend')); bpy.ops.render.render(write_still=True)
