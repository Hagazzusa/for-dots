#!/usr/bin/env python3
"""Independently compare painter ordering to ray/plane depths on a screen grid."""
import json
from pathlib import Path
import build as b

def cross(a,c):return (a[1]*c[2]-a[2]*c[1],a[2]*c[0]-a[0]*c[2],a[0]*c[1]-a[1]*c[0])
def inside(x,y,points):
 q=list(map(b.project,points)); signs=[]
 for i,a in enumerate(q):
  c=q[(i+1)%len(q)];v=(c[0]-a[0])*(y-a[1])-(c[1]-a[1])*(x-a[0])
  if abs(v)>1e-7:signs.append(v>0)
 return bool(signs) and all(s==signs[0] for s in signs)
ordered=sorted(b.faces,reverse=True,key=lambda q:q[0]); tested=overlaps=bad=0
for y in range(5,b.H,10):
 for x in range(5,b.W,10):
  d=tuple(b.F[i]+(x-b.cx)/b.f*b.R[i]-(y-b.cy)/b.f*(1 if i==2 else 0) for i in range(3));hits=[]
  for j,(_,points,col) in enumerate(ordered):
   if not inside(x,y,points):continue
   a,c,e=points[:3];n=cross(tuple(c[i]-a[i] for i in range(3)),tuple(e[i]-a[i] for i in range(3)))
   den=b.dot(n,d)
   if abs(den)<1e-10:continue
   t=b.dot(n,tuple(a[i]-b.C[i] for i in range(3)))/den
   if t>0:hits.append((j,t))
  if hits:
   tested+=1
   if len(hits)>1:
    overlaps+=1
    if hits[-1][1]>min(t for j,t in hits)+1e-7:bad+=1
r={'screen_grid_step_px':10,'samples_covering_faces':tested,'overlapping_face_samples':overlaps,'incorrect_painter_occlusion_samples':bad,'scope':'유한 격자에서 SVG 면 순서와 카메라 광선-평면 교차 깊이를 비교. 모든 픽셀의 증명은 아님.'}
Path(__file__).with_name('occlusion_check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r);assert bad==0
