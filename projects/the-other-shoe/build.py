"""한 짝의 뒤편: 같은 종이 레이어를 두 창에서 보는 140×80×110 mm 수선집."""
from pathlib import Path
import json, math, argparse
ROOT=Path(__file__).resolve().parent
# 모든 좌표는 mm. x: 가로, y: 앞에서 뒤, z: 바닥에서 위.
COLORS={'ink':'#293837','paper':'#eee3cc','wall':'#d9c9aa','wood':'#a77f57','edge':'#6a513c','shoe':'#4e4039','sole':'#282b2c','stitch':'#7bafa6','heel':'#cda06b','clamp':'#b25e43','metal':'#586b69'}
SHAPES=[]
def poly(name,layer,pts,color):SHAPES.append(dict(name=name,y=layer,points=pts,color=COLORS.get(color,color)))
def rect(name,y,x,z,w,h,color):poly(name,y,[(x,z),(x+w,z),(x+w,z+h),(x,z+h)],color)
# 앞면의 두 창은 40×56mm이며 중심은 x=±36, z=60이다.
for x,w in [(-70,14),(-16,32),(56,14)]:rect('front_upright',0,x,32,w,56,'ink')
for z,h in [(0,32),(88,22)]:rect('front_crossbar',0,-70,z,140,h,'ink')
# 한 장으로 자르는 선반. 구두 윤곽이 선반과 연결되어 별도 지지대가 필요 없다.
rect('shelf_base',28,-70,0,140,32,'wood')
rect('shelf_lip',27.98,-70,28,140,4,'edge')
# 기다리는 구두. 뒤꿈치 왼쪽, 앞코 오른쪽.
shoe=[(-55,32),(-55,48),(-51,53),(-46,52),(-43,44),(-37,43),(-32,40),(-24,39),(-20,36),(-20,32)]
poly('waiting_shoe',27.96,shoe,'shoe')
poly('waiting_sole',27.94,[(-55,32),(-20,32),(-20,34),(-54,35)],'sole')
poly('waiting_welt',27.92,[(-53,35),(-22,34.5),(-22,35.2),(-53,35.7)],'heel')
for k in range(3):poly('waiting_lace',27.90,[(-43+k*2,43-k),(-40+k*2,42-k),(-40+k*2,42.7-k),(-43+k*2,43.7-k)],'paper')
for k in range(2):poly('waiting_stitch',27.88,[(-49+k*3,39),(-47+k*3,41.4),(-46.3+k*3,40.9),(-48.3+k*3,38.5)],'stitch')
# 중간 장: 작업대 앞벽 + 가림용 보관장. 둘은 하나의 연결된 종이 조각.
rect('counter_base',48,-70,0,140,25,'wood')
rect('cabinet',48,5,25,29,75,'ink')
for z in [30,48,66,84]:
 rect('drawer',47.98,8,z,23,13,'edge');rect('drawer_pull',47.96,17,z+5,5,2,'heel')
# 공통 뒤판과 인쇄 그림. 뒤 구두는 뒤판에 인쇄되어 별도 잘라 붙일 부품이 아니다.
rect('back_panel',80,-70,0,140,110,'wall')
for z in [18,38,58,78,98]:rect('wall_course',79.98,-70,z,140,.35,'#c4b492')
rect('backbench_front',79.96,34,0,34,33,'wood');rect('backbench_top',79.94,33,33,35,3,'edge')
# 앞 구두를 거울 방향으로 옮긴 짝. 같은 두 바늘땀을 남긴다.
def mate(points):return [(64-(x+55)*.8,40+(z-32)*.8) for x,z in points]
poly('repair_shoe',79.92,mate(shoe),'shoe')
poly('repair_sole',79.90,mate([(-55,32),(-20,32),(-20,34),(-54,35)]),'sole')
poly('repair_welt',79.88,mate([(-53,35),(-22,34.5),(-22,35.2),(-53,35.7)]),'heel')
for k in range(3):poly('repair_lace',79.86,mate([(-43+k*2,43-k),(-40+k*2,42-k),(-40+k*2,42.7-k),(-43+k*2,43.7-k)]),'paper')
for k in range(2):poly('repair_stitch',79.84,mate([(-49+k*3,39),(-47+k*3,41.4),(-46.3+k*3,40.9),(-48.3+k*3,38.5)]),'stitch')
# 새 굽과 ㄷ자 집게: 굽 옆면은 가리지 않는다.
rect('fresh_heel',79.82,58,35.8,6,4.2,'heel')
poly('clamp_body',79.80,[(64,34),(67,34),(67,49),(61,49),(61,47),(65,47),(65,36),(60,36),(60,34)],'clamp')
rect('clamp_screw',79.78,60.4,31,1.3,7,'metal');rect('clamp_foot',79.76,58,31,6,1.3,'metal')
# 인쇄된 공구 실루엣. 시각적인 배경이며 별도 종이 지지부가 아니다.
poly('awl',79.74,[(43,73),(45,74),(47,67),(46,64),(47,57),(45.7,57),(44.8,64),(43,66)],'metal')
rect('peg_rail',79.72,38,80,28,3,'edge')
SPEC={'width_mm':140,'depth_mm':80,'height_mm':110,'card_thickness_mm':.35,'layers_y_mm':[0,28,48,80],'eyes':{'left':[-36,-12,60],'right':[36,-12,60]},'holes':[[-56,-16,32,88],[16,56,32,88]],'shapes':SHAPES}
def write_sources(out):
 out.mkdir(parents=True,exist_ok=True);(out/'model.json').write_text(json.dumps(SPEC,ensure_ascii=False,indent=2)+'\n')
 # mm 단위 SVG 부품 원본. 인쇄용 PDF로 배치하기 전의 부품별 데이터.
 for title,y in [('front',0),('shelf',28),('counter',48),('back',80)]:
  ys=[s for s in SHAPES if (y==0 and s['y']==0) or (y-1<s['y']<=y and y!=0)]
  parts=['<svg xmlns="http://www.w3.org/2000/svg" width="156mm" height="126mm" viewBox="-78 -118 156 126">','<rect x="-62" y="0" width="124" height="8" fill="#e6dbc4"/>']
  for s in ys:
   pts=' '.join(f'{x},{-z}' for x,z in s['points']);parts.append(f'<polygon points="{pts}" fill="{s["color"]}"/>')
  parts.append('<path d="M-62 0H62" stroke="#777" stroke-width=".2" stroke-dasharray="2 1"/>');parts.append('</svg>')
  (out/f'{title}.svg').write_text('\n'.join(parts)+'\n')
def build_blender(out):
 import bpy
 from mathutils import Vector
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 mats={}
 def mat(color):
  if color in mats:return mats[color]
  m=bpy.data.materials.new(color)
  def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
  m.diffuse_color=tuple(lin(int(color[i:i+2],16)/255) for i in (1,3,5))+(1,);m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.88
  mats[color]=m;return m
 for s in SHAPES:
  mesh=bpy.data.meshes.new(s['name']);mesh.from_pydata([(x*.001,s['y']*.001,z*.001) for x,z in s['points']],[],[list(range(len(s['points'])))])
  mesh.update();obj=bpy.data.objects.new(s['name'],mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat(s['color']))
  obj.visible_shadow=s['name'] in ['front_upright','front_crossbar','shelf_base','waiting_shoe','cabinet','counter_base','back_panel']
  # 앞에서 보아 단면 그림. 종이 두께는 주요 지지면에만 추가한다.
  if s['name'] in ['front_upright','front_crossbar','shelf_base','cabinet','counter_base','back_panel']:
   mod=obj.modifiers.new('종이 두께','SOLIDIFY');mod.thickness=.00035;mod.offset=-1
 def box(name,loc,size,color):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat(color));return o
 box('base',(0,.040,-.0006),(.141,.081,.0012),COLORS['paper'])
 for x in [-.0705,.0705]:box('side',(x,.040,.055),(.0007,.080,.110),COLORS['paper'])
 # 열린 윗면으로 빛이 들어오는 실제 만들 수 있는 상자 구도.
 box('ground',(0,.04,-.002),(.8,.8,.001), '#eee9df')
 world=bpy.data.worlds.new('밝은 주변');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
 ld=bpy.data.lights.new('넓은 창','AREA');lo=bpy.data.objects.new('넓은 창',ld);bpy.context.collection.objects.link(lo);lo.location=(-.10,-.04,.25);ld.energy=.5;ld.size=.3
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=192;s.cycles.use_denoising=False;s.cycles.seed=18;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
 s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
 cams=[]
 for name,eye in SPEC['eyes'].items():
  bpy.ops.object.camera_add(location=tuple(v*.001 for v in eye));cam=bpy.context.object;cam.name='view_'+name
  target=(-.037,.028,.042) if name=='left' else (.050,.080,.046)
  cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=30;cam.data.sensor_width=36;cam.data.clip_start=.0001;cam.data.clip_end=5;cams.append((name,cam,1200,1200))
 bpy.ops.object.camera_add(location=(-.23,-.29,.24));cam=bpy.context.object;cam.name='assembled';cam.rotation_euler=(Vector((0,.035,.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.26;cam.data.clip_start=.001;cams.append(('assembled',cam,1600,1400))
 s.camera=cams[-1][1];s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.filepath='//assembled.png'
 bpy.ops.wm.save_as_mainfile(filepath=str(out/'The-Other-Shoe.blend'))
 for name,cam,w,h in cams:
  s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
if __name__=='__main__':
 import sys
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 out=Path(args[0]).resolve() if args else ROOT/'output';write_sources(out)
 if 'bpy' in sys.modules:build_blender(out)
