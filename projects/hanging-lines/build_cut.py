#!/usr/bin/env python3
"""길이 제약 입자로 나눈 줄의 세 시점을 그리는 수치 드로잉 시험이다. 별도 사본에서 실행한다."""
from pathlib import Path
import math,subprocess,json
import numpy as np
from scipy.optimize import brentq
R=Path(__file__).resolve().parent/'output';R.mkdir(parents=True,exist_ok=True)
L=2.35;span=1.6;a=brentq(lambda a:2*a*np.sinh(span/2/a)-L,.1,4)
s=np.linspace(-L/2,L/2,41);x=a*np.arcsinh(s/a);y=a*np.cosh(span/2/a)-a*np.cosh(x/a);initial=np.c_[x,y]
parts=[initial[:21].copy(),initial[20:].copy()];old=[p.copy() for p in parts];lengths=[np.linalg.norm(np.diff(p,axis=0),axis=1) for p in parts];fixed=[0,20];anchors=[p[f].copy() for p,f in zip(parts,fixed)]
snapshots={0:[p.copy() for p in parts]};dt=1/240;maxerr=0
for tick in range(1,240*10+1):
 for k,p in enumerate(parts):
  prev=p.copy();p+=(p-old[k])*math.exp(-.85*dt);p[:,1]+=9.81*dt*dt;old[k]=prev
  for it in range(30):
   p[fixed[k]]=anchors[k]
   for i in range(20):
    delta=p[i+1]-p[i];d=np.linalg.norm(delta);correction=delta*(d-lengths[k][i])/d
    if i==fixed[k]:p[i+1]-=correction
    elif i+1==fixed[k]:p[i]+=correction
    else:p[i]+=.5*correction;p[i+1]-=.5*correction
  p[fixed[k]]=anchors[k]
  maxerr=max(maxerr,float(np.max(abs(np.linalg.norm(np.diff(p,axis=0),axis=1)-lengths[k]))))
 if tick in [120,360,2400]:snapshots[tick]=[p.copy() for p in parts]
for num,tick in enumerate([0,120,2400]):
 paths=[]
 for j in range(9):
  for p in snapshots[tick]:
   pts=[(450+270*(x+.018*(j-4)),90+270*(y+.055*j)) for x,y in p]
   d='M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in pts);paths.append(f'<path d="{d}"/>')
 s='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650"><rect width="900" height="650" fill="#eee9df"/><g fill="none" stroke="#273c40" stroke-width="1.2" stroke-linecap="round">'+''.join(paths)+'</g></svg>'
 p=R/f'cut-{num+1}.svg';p.write_text(s);subprocess.run(['inkscape',str(p),f'--export-filename={p.with_suffix(".png")}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
np.savez(R/'cut_motion.npz',**{str(t):np.stack(p) for t,p in snapshots.items()});(R/'cut_check.json').write_text(json.dumps({'max_segment_length_error':maxerr,'catenary_a':a},indent=2));print(maxerr)
