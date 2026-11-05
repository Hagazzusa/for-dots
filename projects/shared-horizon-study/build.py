#!/usr/bin/env python3
"""A separate camera-projected SVG exercise; no edits to prior artwork."""
import math,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
W,H=1600,1100
C=(2.,-4.,1.); R=(2/math.sqrt(5),1/math.sqrt(5),0); F=(-1/math.sqrt(5),2/math.sqrt(5),0)
f=1500.;cx=650.;cy=370.
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def depth(p):return dot(tuple(p[i]-C[i] for i in range(3)),F)
def project(p):
 v=tuple(p[i]-C[i] for i in range(3));d=dot(v,F);assert d>0
 return cx+f*dot(v,R)/d,cy-f*v[2]/d

def polygon(points,fill,stroke='#465b5c',width=2):
 s=' '.join(f'{x:.5f},{y:.5f}' for x,y in map(project,points))
 return f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>'

def line(a,b,col='#a9b9b0',width=1):
 x,y=project(a);u,v=project(b)
 return f'<path d="M{x:.5f} {y:.5f}L{u:.5f} {v:.5f}" fill="none" stroke="{col}" stroke-width="{width}"/>'

def rotate(p,deg,origin=(0,0,0)):
 a=math.radians(deg);x,y,z=p
 return origin[0]+x*math.cos(a)-y*math.sin(a),origin[1]+x*math.sin(a)+y*math.cos(a),origin[2]+z

faces=[]
def face(points,color,two_sided=False):
 a,b,c=points[:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 toward=tuple(C[i]-a[i] for i in range(3))
 if two_sided or dot(n,toward)>0: faces.append((sum(map(depth,points))/len(points),points,color))
# Cabinet: front is y=-0.4, back y=0.4. Bottom contact is z=0.
front=[(-.45,-.4,0),(.45,-.4,0),(.45,-.4,1.45),(-.45,-.4,1.45)]
face([(.45,.4,0),(-.45,.4,0),(-.45,.4,1.45),(.45,.4,1.45)],'#829b95')
face([(.45,-.4,0),(.45,.4,0),(.45,.4,1.45),(.45,-.4,1.45)],'#8fa79e')
face([(-.45,-.4,1.45),(.45,-.4,1.45),(.45,.4,1.45),(-.45,.4,1.45)],'#d5ddca')
face(front,'#526e70')
# Door panel, rotated around the actual hinge edge, not a hand-fitted quadrilateral.
hinge=(-.45,-.4,.06)
door=[rotate(p,-85,hinge) for p in [(0,0,0),(.88,0,0),(.88,0,1.33),(0,0,1.33)]]
face(door,'#c4cdb2',two_sided=True)
# Independent rotated floor box.
origin=(.86,-.55,0);yaw=25
box=[rotate(p,yaw,origin) for p in [(-.32,-.24,0),(.32,-.24,0),(.32,.24,0),(-.32,.24,0),(-.32,-.24,.42),(.32,-.24,.42),(.32,.24,.42),(-.32,.24,.42)]]
for ids,col in [([0,1,5,4],'#cbb485'),([1,2,6,5],'#b19b73'),([4,5,6,7],'#e4cfa1'),([3,0,4,7],'#b6a17a'),([2,3,7,6],'#b7a079')]:face([box[i] for i in ids],col)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>같은 눈높이 · 원근 연습</title><desc>수치 카메라로 투영한 열린 수납장과 회전한 상자. 원근 검토용 독립 시제품.</desc><path fill="#e4e7dd" d="M0 0H1600V1100H0Z"/>']
svg.append(f'<path d="M0 {cy}H1600" stroke="#a5b5ae" stroke-width="1" stroke-dasharray="8 10"/>')
svg.append(polygon([(-3,-2,0),(3,-2,0),(3,4,0),(-3,4,0)],'#d2dbcf','none'))
for i in range(-5,7):
 svg.append(line((i*.5,-2,0),(i*.5,4,0)))
for j in range(-4,9):svg.append(line((-3,j*.5,0),(3,j*.5,0)))
for _,points,color in sorted(faces,reverse=True,key=lambda x:x[0]):svg.append(polygon(points,color))
# Real hinge axis; marked endpoints remain fixed for every door angle.
svg.append(line(hinge,(-.45,-.4,1.39),'#526c68',5))
# Visible floor contacts and a recessed handle on the door's own plane.
ha=rotate((.75,-.005,.61),-85,hinge);hb=rotate((.75,-.005,.78),-85,hinge)
svg.append(line(ha,hb,'#718674',6))
contacts=[front[0],front[1],box[0],box[1]]
for p in [front[0],box[0],box[1]]:
 x,y=project(p);svg.append(f'<circle cx="{x:.5f}" cy="{y:.5f}" r="4" fill="#a87547"/>')
svg.append('</svg>');(P/'study.svg').write_text('\n'.join(svg))
# Exact numeric checks: same horizon, orthogonal VP condition, hinge invariance.
vp={}
for name,a in [('cabinet_width',0),('cabinet_depth',90),('box_width',25),('box_depth',115),('door_width',-85)]:
 a=math.radians(a);d=(math.cos(a),math.sin(a),0);vp[name]=[cx+f*dot(d,R)/dot(d,F),cy]
assert all(abs(v[1]-cy)<1e-9 for v in vp.values())
for a,b in [('cabinet_width','cabinet_depth'),('box_width','box_depth')]:assert abs((vp[a][0]-cx)*(vp[b][0]-cx)+f*f)<1e-6
assert all(abs(p[2])<1e-12 for p in [*front[:2],*box[:4]])
for angle in range(-90,1):
 for z in [0,1.33]:
  assert max(abs(a-b) for a,b in zip(rotate((0,0,z),angle,hinge),(-.45,-.4,.06+z)))<1e-12
# Door swept region is bounded by x <= hinge_x + door_width; box entirely farther right.
clearance=min(p[0] for p in box)-(-.45+.88)
assert clearance>0
report={'camera':{'position':C,'right':R,'forward':F,'focal_px':f,'principal':[cx,cy]},'horizon_y':cy,'vanishing_points':vp,'ground_contacts_world':contacts,'ground_contact_projection':[project(p) for p in contacts],'door_angle_degrees':-85,'door_hinge_world':hinge,'box_yaw_degrees':yaw,'door_box_minimum_x_separation_bound':clearance,'checks':{'shared_horizon':True,'orthogonal_vp_condition':True,'ground_contact_z_zero':True,'hinge_fixed_for_91_angles':True,'door_box_sweep_disjoint_by_x_bound':True},'limits':['구성용 가상 단위이며 실제 제품 치수나 접근성 인증이 아니다.','SVG는 깊이 버퍼 대신 평균 깊이 순서로 평면을 그린다. 겹침은 별도의 표본 검사와 시각 검토가 필요하다.','재질·조명·그림자 시뮬레이션은 포함하지 않는다.']}
(P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['inkscape',str(P/'study.svg'),'--export-type=png',f'--export-filename={P/"study.png"}','--export-width=1200'],check=True,capture_output=True)
print(json.dumps(report,ensure_ascii=False))
