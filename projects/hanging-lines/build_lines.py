#!/usr/bin/env python3
"""평행선의 밀도·삭제·굴곡 세 변형을 생성한다. 별도 사본에서 실행한다."""
from pathlib import Path
import math,subprocess
R=Path(__file__).resolve().parent/'output';R.mkdir(parents=True,exist_ok=True)
for variant in range(3):
 paths=[]
 n=[46,29,67][variant]
 for j in range(n):
  v=j/(n-1);segments=[];pts=[]
  for i in range(401):
   u=-1+2*i/400
   x=u*(1-.13*v)+.05*math.sin(2*math.pi*v)*(1-u*u)
   y=.22*u+1.36*v+.46*(1-u*u)*(1-.4*v)
   z=.25*math.sin(2.3*u+3*v)*(1-u*u)*math.sin(math.pi*v)+.16*u*v
   if variant==2:y+=.12*math.sin(3*math.pi*u+2*v)*(1-u*u)*math.sin(math.pi*v)
   sx=450+300*(x*.94-z*.34);sy=145+300*(y*.97+z*.18+x*.13)
   if variant==1 and (.25<v<.72) and abs(u-.15*math.sin(v*6))<.18:
    if pts:segments.append(pts);pts=[]
   else:pts.append((sx,sy))
  if pts:segments.append(pts)
  for pts in segments:
   d='M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in pts)
   paths.append(f'<path d="{d}"/>')
 s='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="800" viewBox="0 0 900 800"><rect width="900" height="800" fill="#eee9df"/><g fill="none" stroke="#273c40" stroke-width="1.15" stroke-linecap="round">'+''.join(paths)+'</g></svg>'
 p=R/f'study-{variant+1}.svg';p.write_text(s);subprocess.run(['inkscape',str(p),f'--export-filename={p.with_suffix(".png")}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
