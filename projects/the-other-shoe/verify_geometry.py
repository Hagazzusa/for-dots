"""JSON 좌표에서 독립적으로 두 시야를 검사한다. 기본 실행은 읽기 전용."""
from pathlib import Path
import json,itertools,sys,math
ROOT=Path(__file__).resolve().parent
spec=json.loads((ROOT/'output/model.json').read_text())
def point_on_plane(eye,target,y):
 t=(y-eye[1])/(target[1]-eye[1]);return [eye[0]+t*(target[0]-eye[0]),eye[2]+t*(target[2]-eye[2])]
def inside(p,polygon):
 x,z=p;hit=False
 for a,b in zip(polygon,polygon[1:]+polygon[:1]):
  # 경계도 가림으로 취급한다.
  cross=(x-a[0])*(b[1]-a[1])-(z-a[1])*(b[0]-a[0])
  if abs(cross)<1e-9 and min(a[0],b[0])-1e-9<=x<=max(a[0],b[0])+1e-9 and min(a[1],b[1])-1e-9<=z<=max(a[1],b[1])+1e-9:return True
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def through_front(eye,target):
 x,z=point_on_plane(eye,target,0)
 return any(x0<x<x1 and z0<z<z1 for x0,x1,z0,z1 in spec['holes'])
# 기하학적 가림만 검사한다. 구두 그림의 인지 여부와 밝기는 시각 검토 대상.
blockers=[s for s in spec['shapes'] if s['name'] in ['shelf_base','waiting_shoe','cabinet','counter_base']]
def blocked(eye,target):
 return any(eye[1]<s['y']<target[1] and inside(point_on_plane(eye,target,s['y']),s['points']) for s in blockers)
# 뒤 구두·새 굽·집게의 실제 다각형 내부를 0.5mm 격자로 검사.
targets=[s for s in spec['shapes'] if s['name'] in ['repair_shoe','fresh_heel','clamp_body','clamp_screw','clamp_foot']]
pts=[]
for s in targets:
 xs,zs=zip(*s['points'])
 for ix in range(math.floor(min(xs)*2),math.ceil(max(xs)*2)+1):
  for iz in range(math.floor(min(zs)*2),math.ceil(max(zs)*2)+1):
   if inside([ix/2,iz/2],s['points']):pts.append([ix/2,s['y'],iz/2])
counts={}
for view in ['left','right']:
 rays=visible=0;outside=0
 for offset in itertools.product([-1,0,1],repeat=3):
  eye=[a+b for a,b in zip(spec['eyes'][view],offset)]
  for point in pts:
   rays+=1
   if not through_front(eye,point):outside+=1;continue
   if not blocked(eye,point):visible+=1
 counts[view]={'rays':rays,'visible':visible,'outside_front':outside}
assert counts['left']['visible']==0,counts
assert counts['right']['visible']==counts['right']['rays'],counts
# 앞 구두 전체 꼭짓점은 왼쪽 창을 통과하고 중간 장에 닿기 전에 만난다.
waiting=next(s for s in spec['shapes'] if s['name']=='waiting_shoe')
for off in itertools.product([-1,0,1],repeat=3):
 eye=[a+b for a,b in zip(spec['eyes']['left'],off)]
 for x,z in waiting['points']:assert through_front(eye,[x,waiting['y'],z])
# 제작 부품은 바닥으로 연결된다. 앞면 창 주변 최소 폭 18mm, 가림장 29mm.
assert spec['layers_y_mm']==[0,28,48,80]
assert min(b-a for a,b in zip(spec['layers_y_mm'],spec['layers_y_mm'][1:]))>8
bounds={}
for side,eye in spec['eyes'].items():
 projected=[]
 for off in itertools.product([-1,1],repeat=3):
  e=[a+b for a,b in zip(eye,off)]
  for shape in targets:
   for x,z in shape['points']:projected.append(point_on_plane(e,[x,shape['y'],z],48))
 xs,zs=zip(*projected);bounds[side]={'x_min':min(xs),'x_max':max(xs),'z_min':min(zs),'z_max':max(zs)}
assert 5<bounds['left']['x_min']<bounds['left']['x_max']<34
assert 25<bounds['left']['z_min']<bounds['left']['z_max']<100
assert bounds['right']['x_min']>34
report={'continuous_vertex_bounds_at_cabinet_mm':bounds,'size_mm':[140,80,110],'eye_box_offsets_mm':[-1,0,1],'target_grid_mm':.5,'target_points':len(pts),'views':counts,'front_shoe_left_vertices_tested':270,'minimum_layer_gap_mm':20,'glue_tab_mm':8,'physical_build_tested':False,'limit':'지정한 27개 눈 위치와 다각형 내 0.5mm 격자 표본의 기하 검사. 휘어짐·접착·재단 오차·실물 관찰은 미검증.'}
if '--report' in sys.argv:Path(sys.argv[sys.argv.index('--report')+1]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
