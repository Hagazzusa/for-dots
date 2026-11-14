"""서로 다른 출구: 외부 자산 없이 재생성하는 벡터 원본."""
from pathlib import Path
import math
P = Path(__file__).resolve().parent
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1500" viewBox="0 0 1200 1500">', '<title>서로 다른 출구</title>', '<desc>열린 방향이 차례로 돌아가는 열일곱 개의 남색 원과 바깥에 놓인 주홍 점.</desc>', '<rect width="1200" height="1500" fill="#eee8da"/>']
for j in range(17):
    r = 54 + 23*j
    center = math.radians(-145 + 13*j)
    gap = math.radians(42)
    a, b = center+gap/2, center+2*math.pi-gap/2
    x1,y1 = 600+r*math.cos(a),700+r*math.sin(a)
    x2,y2 = 600+r*math.cos(b),700+r*math.sin(b)
    s.append(f'<path d="M {x1:.4f},{y1:.4f} A {r},{r} 0 1 1 {x2:.4f},{y2:.4f}" fill="none" stroke="#173e52" stroke-width="9" stroke-linecap="butt"/>')
s.append('<circle cx="737" cy="1234" r="27" fill="#d65331"/>')
s.append('</svg>')
(P/'Different-Exits.svg').write_text('\n'.join(s)+'\n', encoding='utf-8')
