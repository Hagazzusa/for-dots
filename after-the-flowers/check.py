#!/usr/bin/env python3
import json,math
from pathlib import Path
import build as b

def inside(x,y,points):
 signs=[]
 for i,a in enumerate(points):
  c=points[(i+1)%len(points)];v=(c[0]-a[0])*(y-a[1])-(c[1]-a[1])*(x-a[0])
  if abs(v)>1e-7:signs.append(v>0)
 return bool(signs) and all(s==signs[0] for s in signs)
data=[]
for q in b.ordered:
 pp=list(map(b.project,q['p']));a,c,d=q['p'][:3];n=b.cross(tuple(c[i]-a[i] for i in range(3)),tuple(d[i]-a[i] for i in range(3)))
 data.append((pp,(min(p[0] for p in pp),min(p[1] for p in pp),max(p[0] for p in pp),max(p[1] for p in pp)),a,n,q['name']))
tested=overlaps=bad=0;badnames={}
for y in range(5,b.H,10):
 for x in range(5,b.W,10):
  origin=tuple((x-b.CX)/b.S*b.R[i]-(y-b.CY)/b.S*b.U[i]-10*b.F[i] for i in range(3));hits=[]
  for j,(pp,box,a,n,name) in enumerate(data):
   if not(box[0]<=x<=box[2] and box[1]<=y<=box[3]) or not inside(x,y,pp):continue
   den=b.dot(n,b.F)
   if abs(den)<1e-12:continue
   t=b.dot(n,tuple(a[i]-origin[i] for i in range(3)))/den
   hits.append((j,t,name))
  if hits:
   tested+=1
   if len(hits)>1:
    overlaps+=1
    if hits[-1][1]>min(h[1] for h in hits)+1e-7:
     bad+=1;k=hits[-1][2];badnames[k]=badnames.get(k,0)+1
report={'sample_spacing_px':10,'samples_on_object_faces':tested,'overlap_samples':overlaps,'wrong_painter_order_samples':bad,'wrong_order_by_part':badnames,'limits':'유한 격자 표본 검사. 선/접촉색면·픽셀 경계·모든 시점의 증명은 아니다. 같은 카메라를 공유하되 깊이는 광선-평면 교차로 비교한다.'}
Path(__file__).with_name('occlusion_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report)
assert bad==0
