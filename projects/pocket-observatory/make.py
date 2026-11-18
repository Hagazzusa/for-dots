"""주머니의 천문대 — 외부 이미지 없는 벡터 원본 생성."""
from pathlib import Path
import random
r=random.Random(19)
a=['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1400" viewBox="0 0 1200 1400"><title>주머니의 천문대</title><desc>남색 주머니에 놓인 동전, 단추, 열쇠와 작은 표가 밤하늘처럼 보이는 그림.</desc><rect width="1200" height="1400" fill="#efe6d1"/><path d="M130 140 Q600 95 1070 140 L1010 1080 Q820 1260 600 1300 Q380 1260 190 1080Z" fill="#203b4d"/><path d="M158 165 Q600 127 1042 165 L983 1065 Q800 1233 600 1272 Q400 1233 217 1065Z" fill="none" stroke="#b7b4a0" stroke-width="3" stroke-dasharray="9 12"/><path d="M135 230 Q600 184 1065 230" fill="none" stroke="#102d3e" stroke-width="14"/><path d="M150 220 Q600 175 1050 220" fill="none" stroke="#6b8084" stroke-width="3" stroke-dasharray="10 12"/>''']
# 실밥은 별처럼 보이지만 일정한 직물 방향을 유지한다.
for _ in range(210):
 x=r.randint(235,965); y=r.randint(280,1120)
 if y>1050 and abs(x-600)>250: continue
 a.append(f'<path d="M{x} {y} l{r.randint(2,5)} -2" stroke="#56717b" stroke-width="1.5" opacity=".6"/>')
a+=['''<g transform="translate(392 457)"><circle cx="8" cy="14" r="93" fill="#112c3a"/><circle r="93" fill="#d5a34f"/><circle r="79" fill="none" stroke="#f0c97c" stroke-width="3"/><path d="M-48 28 Q0 -71 48 28 M-59 40 H59 M-39 47 H39" fill="none" stroke="#96703d" stroke-width="7"/><circle cy="-29" r="10" fill="#f2cf84"/></g>
<g transform="translate(818 661) rotate(-21)"><ellipse cy="9" rx="92" ry="88" fill="#112c3a"/><circle r="87" fill="#c45d43"/><circle r="68" fill="none" stroke="#e18b66" stroke-width="4"/><g fill="#203b4d"><circle cx="-20" cy="-20" r="10"/><circle cx="20" cy="-20" r="10"/><circle cx="-20" cy="20" r="10"/><circle cx="20" cy="20" r="10"/></g><path d="M-20 -20 L20 20 M20 -20 L-20 20" stroke="#e8d6b4" stroke-width="4"/><path d="M-115 5 C-155 60 142 85 118 -4" fill="none" stroke="#e8d6b4" stroke-width="3"/></g>
<g transform="translate(450 850) rotate(-29)"><path d="M0 0 L0 212 L35 212 L35 190 L17 190 L17 160 L40 160 L40 138 L17 138 L17 0" fill="#aaaea0"/><circle r="57" fill="#b9c1b5"/><circle r="31" fill="#203b4d"/><path d="M-37 -26 A45 45 0 0 1 28 -35" fill="none" stroke="#edf0d8" stroke-width="5"/></g>
<g transform="translate(754 363) rotate(24)"><path d="M-55 -62 H55 V-20 Q32 -8 55 5 V64 H-55 V5 Q-32 -8 -55 -20Z" fill="#e6d9b4"/><path d="M-38 29 H38" stroke="#b96a4b" stroke-width="4" stroke-dasharray="3 5"/><path d="M-26 -40 H26 M-26 -29 H11 M-26 -18 H20" stroke="#647270" stroke-width="4"/><circle cy="5" r="10" fill="none" stroke="#b96a4b" stroke-width="3"/></g>
<path d="M653 1014 C782 889 943 966 865 1073 C816 1143 700 1112 733 1058 C754 1025 798 1053 769 1073" fill="none" stroke="#d4c8a7" stroke-width="3" stroke-linecap="round"/>
<path d="M609 565 l0 24 M597 577 h24 M285 717 v16 M277 725 h16 M660 819 v12 M654 825 h12" stroke="#d8cfb0" stroke-width="3"/>
</svg>''']
Path(__file__).with_name('Pocket-Observatory.svg').write_text('\n'.join(a),encoding='utf-8')
