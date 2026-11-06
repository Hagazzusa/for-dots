"""서로 다른 굴곡의 물결과 물고기를 그리는 벡터 그림."""
from pathlib import Path
import math, subprocess
P=Path(__file__).resolve().parent
O=P/'output'; O.mkdir(exist_ok=True)
W,H=1100,1400
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1400" viewBox="0 0 1100 1400" role="img" aria-labelledby="title desc">', '<title id="title">물살을 가로질러</title>', '<desc id="desc">어두운 청록 물결이 비스듬히 흐르는 밝은 화면에서 주홍 물고기 한 마리가 왼쪽 아래를 향한다.</desc>', '<rect width="1100" height="1400" fill="#eee8d5"/>', '<defs><clipPath id="frame"><rect x="65" y="65" width="970" height="1270"/></clipPath></defs>', '<g clip-path="url(#frame)">']
# 물결은 유체 해가 아니라 손으로 정한 곡선식이다.
for j in range(-18,89):
    pts=[]
    for x in range(-100,1201,7):
        y=j*21 + 0.40*x + 39*math.sin(x/195+j*.13)+13*math.sin(x/77+j*.31)
        pts.append((x,y))
    d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in pts)
    sw=3.1+1.5*(.5+.5*math.sin(j*.58))
    s.append(f'<path d="{d}" fill="none" stroke="#174d4c" stroke-width="{sw:.2f}"/>')
# 물고기는 하나만 두어 무늬의 반복보다 횡단 방향을 드러낸다.
fish=[(543,710,-40,1.80)]
for n,(x,y,angle,scale) in enumerate(fish):
    s.append(f'<g id="fish-{n+1}" transform="translate({x} {y}) rotate({angle}) scale({scale})">')
    # 밝은 테두리로 물결과 물고기의 윤곽을 분리한다.
    body='M -122,0 C -69,-67 6,-55 80,-11 L 131,-49 Q 119,-9 136,34 L 80,12 C 3,55 -78,49 -122,0 Z'
    s.append(f'<path d="{body}" fill="#d64b32" stroke="#eee8d5" stroke-width="13" stroke-linejoin="round"/>')
    s.append('<path d="M -40,-39 Q -8,-80 17,-44 M 5,39 Q 29,67 47,29" fill="#d64b32" stroke="#eee8d5" stroke-width="7" stroke-linejoin="round"/>')
    s.append('<path d="M -67,-28 Q -39,0 -65,28" fill="none" stroke="#eee8d5" stroke-width="4"/>')
    s.append('<circle cx="-88" cy="-8" r="4.8" fill="#174d4c"/>')
    s.append('<path d="M -10,2 Q 19,-5 39,8 L 12,20 Z" fill="#eee8d5"/>')
    s.append('</g>')
s.extend(['</g>','</svg>'])
svg=O/'Across-the-Current.svg'; svg.write_text('\n'.join(s)+'\n')
subprocess.run(['inkscape',str(svg),'--export-filename='+str(O/'Across-the-Current.png'),'--export-width=1100'],check=True,stdout=subprocess.DEVNULL)
