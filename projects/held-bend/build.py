#!/usr/bin/env python3
"""띠 매듭의 세 변형을 같은 시점과 배율로 만드는 보류 연구.

Python, NumPy, Inkscape가 필요하다. 기존 결과를 보존하려면 별도 사본에서 실행한다.
이 코드는 삼차원 띠의 투영 면을 깊이순으로 그리는 시각 실험이며 물리 시뮬레이션이 아니다.
"""
import numpy as np
from pathlib import Path
import argparse
import subprocess
import tempfile
import os
from PIL import Image
ROOT=Path(__file__).resolve().parent


def make_svg(variant):
 N=720
 t=np.arange(N)*2*np.pi/N
 c=np.column_stack((np.sin(t)+2*np.sin(2*t),np.cos(t)-2*np.cos(2*t),-.65*np.sin(3*t)))
 c[:,0]*=1.18+.20*np.cos(t-.7)
 c[:,1]*=.88+.14*np.sin(t+.4)
 c[:,0]+=.07*c[:,1]**2
 if variant==3:
  c[:,1]+=.78*np.logaddexp(0,8*(-c[:,1]-1.0))/8
  c[:,0]-=.5*np.exp((np.cos(t-np.pi)-1)/.45)
 T=np.roll(c,-1,axis=0)-np.roll(c,1,axis=0);T/=np.linalg.norm(T,axis=1)[:,None]
 u=np.cross(T,[0,0,1]);u/=np.linalg.norm(u,axis=1)[:,None];v=np.cross(T,u)
 beta=(2.3 if variant==1 else 3.1)*np.exp((np.cos(t-4.8)-1)/(.13 if variant==1 else .23))+.22*np.sin(t)
 u=u*np.cos(beta)[:,None]+v*np.sin(beta)[:,None]
 w=.66*(1+.12*np.cos(t-2)+(0 if variant==1 else .4)*np.exp((np.cos(t-4.8)-1)/.23))
 a=.30;b=-.22
 Rx=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
 Rz=np.array([[np.cos(b),-np.sin(b),0],[np.sin(b),np.cos(b),0],[0,0,1]])
 R=Rz@Rx
 c=c@R.T;u=u@R.T
 p=c-u*w[:,None]/2;q=c+u*w[:,None]/2
 scale=88
 proj=lambda a: np.column_stack([425+scale*a[:,0],460-scale*a[:,1]])
 P,Q=proj(p),proj(q)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900" viewBox="0 0 900 900">','<rect width="900" height="900" fill="#f1ebdd"/>']
 for i in np.argsort(c[:,2]):
  j=(i+1)%N
  normal=np.cross(c[j]-c[i],q[i]-p[i]);normal/=np.linalg.norm(normal)
  base=np.array([38,91,91]) if normal[2]<0 else np.array([190,134,70])
  k=.82+.18*abs(np.dot(normal,[-.35,.3,.887]))
  col='#'+''.join(f'{int(x):02x}' for x in base*k)
  points=[P[i],Q[i],Q[j],P[j]]
  s=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
  svg.append(f'<polygon points="{s}" fill="{col}" stroke="{col}" stroke-width="1.2" stroke-linejoin="round"/>')
  for k in [.12,.25,.40,.60,.75,.88]:
   x=P[i]*(1-k)+Q[i]*k;y=P[j]*(1-k)+Q[j]*k
   svg.append(f'<path d="M{x[0]:.3f},{x[1]:.3f} L{y[0]:.3f},{y[1]:.3f}" fill="none" stroke="#e0d6b9" stroke-opacity=".20" stroke-width=".6"/>')
 svg.append('</svg>')
 return '\n'.join(svg)


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,default=ROOT/'output')
 args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
 panels=[]
 for variant in (1,2,3):
  svg=make_svg(variant)
  (out/f'variant-{variant}.svg').write_text(svg,encoding='utf-8')
  inner=svg[svg.index('>')+1:svg.rfind('</svg>')]
  panels.append(f'<g transform="translate({(variant-1)*500},0) scale({500/900})">{inner}</g>')
 overview='<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="500" viewBox="0 0 1500 500"><title>띠 매듭 형태 연구</title><desc>왼쪽부터 작은 뒤집힘, 넓힌 뒤집힘, 누른 아래 고리</desc>'+''.join(panels)+'</svg>'
 (out/'comparison.svg').write_text(overview,encoding='utf-8')
 with tempfile.TemporaryDirectory(prefix='held-bend-') as td:
  env=dict(os.environ,HOME=td,XDG_CACHE_HOME=td)
  comparison=Image.new('RGB',(1500,500),(241,235,221))
  for variant in (1,2,3):
   preview=Path(td)/f'{variant}.png'
   subprocess.run(['inkscape',str(out/f'variant-{variant}.svg'),'--export-filename='+str(preview),'-w','500'],check=True,stdout=subprocess.DEVNULL,env=env)
   with Image.open(preview) as image:comparison.paste(image.convert('RGB'),((variant-1)*500,0))
  comparison.save(out/'comparison.png')
 print(out)

if __name__=='__main__':main()
