"""수치 망의 두 크롭과 드로잉 해석. 느슨한 곡선은 물성 해석이 아닙니다."""
from pathlib import Path
import json,numpy as np,subprocess
P=Path(__file__).resolve().parent
OUT=P/'output/ink-study'
OUT.mkdir(parents=True,exist_ok=True)
d=json.loads((P/'output/net/model.json').read_text());p=np.array(d['after']);edges=np.delete(np.array(d['edges']),d['cut_edge_index'],axis=0);rest=np.delete(np.array(d['rest_lengths']),d['cut_edge_index'])
views=[('near','0.27 0.17 1.0 1.08',900,1050),('fragment','0.35 0.10 .76 .63',912,756)]
for name,view,width_px,height_px in views:
 body=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="{view}">',f'<rect x="-2" y="-2" width="5" height="5" fill="#f6f2e9"/>','<g fill="none" stroke="#263c44" stroke-linecap="round">']
 for (a,b),r in zip(edges,rest):
  v=p[b]-p[a];length=np.linalg.norm(v);tension=max(length-r,0)*180
  width=.0012+.0015*np.sqrt(min(tension/3.8,1))
  if r-length>1e-6:
   sag=np.sqrt(6*length*(r-length))/2
   mid=(p[a]+p[b])/2+[0,sag]
   path=f'M{p[a,0]},{p[a,1]} Q{mid[0]},{mid[1]} {p[b,0]},{p[b,1]}'
  else:path=f'M{p[a,0]},{p[a,1]} L{p[b,0]},{p[b,1]}'
  body.append(f'<path stroke-width="{width}" d="{path}"/>')
 body+=['</g>','</svg>'];f=OUT/(name+'.svg');f.write_text('\n'.join(body))
 subprocess.run(['inkscape',str(f),'--export-type=png','--export-filename='+str(f.with_suffix('.png'))],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
