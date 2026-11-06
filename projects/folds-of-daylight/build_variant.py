"""접힌 평면 패널을 직교 투영하고 평행광 그림자를 SVG로 그린다."""
from pathlib import Path
import math,json,subprocess
import numpy as np
P=Path(__file__).resolve().parent;O=P/'variants';O.mkdir(exist_ok=True)
N=20;start=math.radians(-18);sweep=math.radians(264);inner=.72;outer=3.2
verts=[]
for i in range(N+1):
 a=start+sweep*i/N;k=(.05+.5*(i/N)**1.8) if i%2 else 0
 for r in (inner,outer):verts.append([r*math.cos(a),r*math.sin(a),.04+r*k])
v=np.array(verts);faces=[[2*i,2*i+1,2*i+3,2*i+2] for i in range(N)]
view=np.array([6.2,-9.2,5.8]);view/=np.linalg.norm(view)
right=np.cross([0,0,1],view);right/=np.linalg.norm(right);up=np.cross(view,right)
light=np.array([-3.,-4.,8.]);light/=np.linalg.norm(light)
def project(p):return (700+150*np.dot(p,right),735-150*np.dot(p,up))
def points(poly):return ' '.join('%.3f,%.3f'%project(p) for p in poly)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1400" viewBox="0 0 1400 1400" role="img" aria-labelledby="title desc">','<title id="title">한쪽 끝부터</title>','<desc id="desc">청회색 바탕 위 황금빛 주름의 한쪽은 낮고 반대쪽은 높게 솟는다.</desc>','<rect width="1400" height="1400" fill="#83a6ac"/>','<defs><mask id="shadow" maskUnits="userSpaceOnUse" x="0" y="0" width="1400" height="1400"><rect width="1400" height="1400" fill="black"/>']
for face in faces:
 poly=v[face];shadow=poly-poly[:,2,None]*light/light[2]
 s.append(f'<polygon points="{points(shadow)}" fill="white"/>')
s+=['</mask></defs>','<rect width="1400" height="1400" fill="#25474d" opacity="0.37" mask="url(#shadow)"/>']
for i in sorted(range(N),key=lambda i:np.mean(v[faces[i]]@view)):
 poly=v[faces[i]];normal=np.cross(poly[1]-poly[0],poly[2]-poly[0]);normal/=np.linalg.norm(normal)
 front=np.dot(normal,view)>0;base=np.array([238,161,55] if front else [173,92,35]);normal=normal if front else -normal
 strength=.59+.45*max(0,float(np.dot(normal,light)));rgb=np.clip(base*strength,0,255).astype(int);color='#%02x%02x%02x'%tuple(rgb)
 s.append(f'<polygon id="panel-{i+1}" points="{points(poly)}" fill="{color}" stroke="{color}" stroke-width="0.6" stroke-linejoin="round"/>')
s.append('</svg>');svg=O/'From-One-End.svg';svg.write_text('\n'.join(s)+'\n')
(O/'geometry.json').write_text(json.dumps({'vertices':verts,'faces':faces,'camera_view':view.tolist(),'light_direction':light.tolist(),'parameters':{'panels':N,'inner_radius':inner,'outer_radius':outer,'start_degrees':-18,'sweep_degrees':264,'ridge_profile':'.05+.5*(i/N)**1.8 for odd i; 0 otherwise','base_height':.04}},indent=2)+'\n')
subprocess.run(['inkscape',str(svg),'--export-filename='+str(O/'From-One-End.png')],check=True,stdout=subprocess.DEVNULL)
