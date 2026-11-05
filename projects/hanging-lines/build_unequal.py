#!/usr/bin/env python3
"""높이가 다른 두 지지점과 줄 하나의 절단 초기 0.8초를 그린다. 별도 사본에서 실행한다."""
from pathlib import Path
import numpy as np,math,subprocess
from scipy.optimize import brentq
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent/'output'/'unequal';R.mkdir(parents=True,exist_ok=True)
L=2.35;dx=1.6;dy=.32;a=brentq(lambda a:2*a*np.sinh(dx/2/a)-math.sqrt(L*L-dy*dy),.1,4);b=a*np.arctanh(dy/L);c=a*np.cosh((-.8-b)/a)
s=np.linspace(0,L,61);x=b+a*np.arcsinh(np.sinh((-.8-b)/a)+s/a);y=c-a*np.cosh((x-b)/a);initial=np.c_[x,y];parts=[initial[:31].copy(),initial[30:].copy()];old=[p.copy() for p in parts];lengths=[np.linalg.norm(np.diff(p,axis=0),axis=1) for p in parts];fixed=[0,30];anchors=[p[f].copy() for p,f in zip(parts,fixed)];snaps={0:[p.copy() for p in parts]};dt=1/480
for tick in range(1,385):
 for k,p in enumerate(parts):
  prev=p.copy();p+=(p-old[k])*math.exp(-.3*dt);p[:,1]+=9.81*dt*dt;old[k]=prev
  for it in range(35):
   p[fixed[k]]=anchors[k]
   for i in range(30):
    d=p[i+1]-p[i];length=np.linalg.norm(d);corr=d*(length-lengths[k][i])/length
    if i==fixed[k]:p[i+1]-=corr
    elif i+1==fixed[k]:p[i]+=corr
    else:p[i]+=.5*corr;p[i+1]-=.5*corr
  p[fixed[k]]=anchors[k]
 if tick in [24,48,72,96,144,192,288,384]:snaps[tick]=[p.copy() for p in parts]
for tick,parts in snaps.items():
 paths=[]
 for p in parts:
  d='M'+' L'.join(f'{450+300*x:.3f},{85+300*y:.3f}' for x,y in p);paths.append(f'<path d="{d}"/>')
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650"><rect width="900" height="650" fill="#eee9df"/><g fill="none" stroke="#273c40" stroke-width="2.8" stroke-linecap="round">'+''.join(paths)+'</g></svg>';f=R/f'{tick:03}.svg';f.write_text(svg);subprocess.run(['inkscape',str(f),f'--export-filename={f.with_suffix(".png")}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
canvas=Image.new('RGB',(1800,1350),'#eee9df');draw=ImageDraw.Draw(canvas)
for i,tick in enumerate(snaps):
 with Image.open(R/f'{tick:03}.png') as im:im=im.resize((600,433),Image.Resampling.LANCZOS);canvas.paste(im,(i%3*600,i//3*450+17))
 draw.text((i%3*600+20,i//3*450+6),f'{tick/480:.2f}s',fill='#273c40')
canvas.save(R/'comparison.png');np.savez(R/'motion.npz',**{str(k):np.stack(v) for k,v in snaps.items()})
