"""Coarse front-surface silhouette overlap estimate; not final rendered proof."""
import numpy as np,math
from PIL import Image,ImageDraw
D=[8.0,11.6,9.4,13.0,7.2,10.8,12.4,8.8]
rows=[]
for deg in range(45,76,5):
 for rise in [1.5,2.4,3.2,4.0,4.8]:
  a=math.radians(deg);c=np.array([10*math.sin(a),-10*math.cos(a),2+rise]);target=np.array([0,0,2]);f=target-c;f/=np.linalg.norm(f);r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f);masks=[];xs=[];ys=[]
  for k,t in enumerate(D):
   v=[]
   for radius,angles in [(1.25,np.linspace(k*45+3,k*45+42,25)),(.81,np.linspace(k*45+42,k*45+3,25))]:
    for ang in angles:
     b=math.radians(ang);p=np.array([radius*math.cos(b)*t/10,-10+t,2+radius*math.sin(b)*t/10])-c
     px=(np.dot(p,r)/np.dot(p,f)*48/36+.5)*512;py=(.5-np.dot(p,u)/np.dot(p,f)*48/36)*512;v.append((px,py));xs.append(px);ys.append(py)
   im=Image.new('1',(512,512));ImageDraw.Draw(im).polygon(v,fill=1);masks.append(np.asarray(im,dtype=np.uint8))
  count=sum(masks);area=sum(m.sum() for m in masks);over=(count>1).sum()/area
  crop=min(xs)<30 or max(xs)>482 or min(ys)<30 or max(ys)>482
  rows.append((round(float(over),4),deg,rise,crop,round(max(xs)-min(xs)),round(max(ys)-min(ys))))
print(*sorted(rows)[:15],sep='\n')
