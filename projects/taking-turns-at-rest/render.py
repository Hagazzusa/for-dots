#!/usr/bin/env python3
"""동역학 표본을 고정 시점의 간결한 그림으로 렌더한다."""
from pathlib import Path
import argparse,subprocess
import numpy as np
from PIL import Image,ImageDraw
from model import parameters,geometry,ROOT
BG=(239,234,224);INK=(74,75,72);COLORS=((114,48,61),(54,70,82));SPRING=(143,127,104)

def frame(y,p,time=0,fade=False):
 ss=p['supersample'];W,H=p['width'],p['height'];im=Image.new('RGB',(W*ss,H*ss),BG);d=ImageDraw.Draw(im)
 def xy(a):return tuple(np.rint(np.array([W/2+a[0]*380,170-a[1]*380])*ss).astype(int))
 def line(points,color,width):d.line([xy(a) for a in points],fill=color,width=max(1,round(width*ss)),joint='curve')
 def disk(point,r,color):
  x,y=xy(point);r=r*ss;d.ellipse((x-r,y-r,x+r,y+r),fill=color)
 anchors,bobs,links=geometry(np.asarray(y)[[0,2]],p)
 # 고정 지지대와 두 축. 별도 흔들림이나 그림자를 더하지 않는다.
 line([(-.68,.12),(.68,.12)],INK,2)
 for a,b in zip(anchors,bobs):
  line([(a[0],.12),a],INK,1.4);line([a,b],INK,2)
  disk(a,4,INK)
 delta=links[1]-links[0];length=np.linalg.norm(delta);axis=delta/length;normal=np.array([-axis[1],axis[0]])
 pts=[]
 for u in np.linspace(0,1,160):
  # 양 끝에서 진폭을 줄여 스프링 그림이 연결점에 닿게 한다.
  envelope=np.sin(np.pi*u)**.7
  pts.append(links[0]+u*delta+.016*envelope*np.sin(2*np.pi*12*u)*normal)
 line(pts,SPRING,1.5)
 for a in links:disk(a,2.2,SPRING)
 for i,b in enumerate(bobs):
  disk(b,20,COLORS[i]);disk((b[0]-.014,b[1]+.015),2.0,tuple(min(255,x+22) for x in COLORS[i]))
 im=im.resize((W,H),Image.Resampling.LANCZOS)
 if fade and time>p['duration_s']-1/p['fps']-.65:
  amount=0 if time>=p['duration_s']-1/p['fps']-1e-7 else max(0,min(1,(p['duration_s']-1/p['fps']-time)/.65));im=Image.blend(Image.new('RGB',(W,H),BG),im,amount)
 return im

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int);ap.add_argument('--preview',type=float);args=ap.parse_args();p=parameters()
 motion=np.loadtxt(ROOT/'motion.csv',delimiter=',',skiprows=1)
 out=ROOT/'tmp/frames';out.mkdir(parents=True,exist_ok=True)
 if args.preview is not None:
  i=min(len(motion)-1,max(0,round(args.preview*p['fps'])));dest=ROOT/'tmp'/f'preview-{i:04d}.png';frame(motion[i,1:],p).save(dest);print(dest);return
 for i in range(args.start,min(args.stop or len(motion),len(motion))):frame(motion[i,1:],p,motion[i,0],True).save(out/f'{i:05d}.png')
 print(args.start,min(args.stop or len(motion),len(motion)))
if __name__=='__main__':main()
