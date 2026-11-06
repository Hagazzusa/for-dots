"""화면의 4픽셀 간격 표본에서 화가 알고리즘의 깊이 순서를 비교한다."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import numpy as np
P=Path(__file__).resolve().parent
m=json.loads((P/'output/geometry.json').read_text());v=np.array(m['vertices']);faces=m['faces'];view=np.array(m['camera_view']);right=np.cross([0,0,1],view);right/=np.linalg.norm(right);up=np.cross(view,right)
xy=np.column_stack([700+150*(v@right),735-150*(v@up)]);depth=v@view
root=ET.parse(P/'output/Folds-of-Daylight.svg').getroot();order=[int(p.attrib['id'].split('-')[1])-1 for p in root.findall('{http://www.w3.org/2000/svg}polygon')]
assert sorted(order)==list(range(24))
x,y=np.meshgrid(np.arange(2,1400,4),np.arange(2,1400,4));x=x.ravel();y=y.ravel();nearest=np.full(x.shape,-np.inf);true=np.full(x.shape,-1,dtype=int);paint=np.full(x.shape,-1,dtype=int)
for fi in order:
 face=faces[fi]
 for inds in [(face[0],face[1],face[2]),(face[0],face[2],face[3])]:
  a,b,c=xy[list(inds)];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);assert abs(den)>1e-7
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;w=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;t=1-u-w
  inside=(u>=0)&(w>=0)&(t>=0);z=u*depth[inds[0]]+w*depth[inds[1]]+t*depth[inds[2]]
  update=inside&(z>nearest+1e-7);nearest[update]=z[update];true[update]=fi;paint[inside]=fi
bad=int(np.sum((true>=0)&(paint!=true)))
assert bad==0,bad
print(json.dumps({'표본 수':len(x),'면 내부 표본':int(np.sum(true>=0)),'깊이 순서 불일치':bad,'한계':'4픽셀 간격 표본이며 전 픽셀 증명·광선 추적·자기 그림자 검증이 아닙니다.'},ensure_ascii=False,indent=2))
