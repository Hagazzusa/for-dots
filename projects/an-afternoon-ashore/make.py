"""손으로 정한 도형과 고정 시드로 벡터 판화풍 그림을 만듭니다."""
from pathlib import Path
import random
import math
ROOT = Path(__file__).resolve().parent
rng = random.Random(1706)
s = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1080" viewBox="0 0 1440 1080">
<title>배를 말리는 오후</title><desc>모래 위에 뒤집어 놓은 네 척의 배. 오른쪽 물가에는 빈 자국 하나가 남아 있다.</desc>
<defs><clipPath id="paper"><rect x="65" y="65" width="1310" height="950"/></clipPath></defs>
<rect width="1440" height="1080" fill="#f3eddb"/>
<g clip-path="url(#paper)">
<rect x="65" y="65" width="1310" height="950" fill="#dcae6c"/>
<path d="M1060 35 C1020 160 1140 270 1090 401 S1010 610 1144 736 S1230 926 1170 1060 L1490 1090 1490 20 Z" fill="#244d64"/>
<path d="M1050 60 C1010 180 1120 286 1071 405 S995 610 1124 744 S1210 930 1152 1030" fill="none" stroke="#e9d8ac" stroke-width="16"/>
''']
# 해변의 결: 도형을 가리지 않는 짧고 드문 흔적
for i in range(950):
    x,y=rng.uniform(70,1370),rng.uniform(70,1010)
    s.append(f'<path d="M{x:.2f} {y:.2f} l{rng.uniform(1,5):.2f} {rng.uniform(-1,1):.2f}" stroke="#8c734f" stroke-opacity=".16" stroke-width="1.1"/>')
# 물의 조각난 선. 서로 다른 길이와 비대칭 배치.
for i in range(46):
    y=95+i*20
    x=1257+22*math.sin(i*.8)
    s.append(f'<path d="M{x} {y} q25 -9 {rng.uniform(38,97)} -1" fill="none" stroke="#78a2a3" stroke-width="2" opacity=".65"/>')
# 배가 빠져나간 자리. 비어 있는 중심이 다섯 번째 배처럼 읽힌다.
s.append('''<g transform="translate(935 710) rotate(-28)">
<path d="M0 -175 C-83 -99 -87 50 -56 158 Q0 189 56 158 C87 50 83 -99 0 -175 Z" fill="#c89659" opacity=".55"/>
<path d="M-17 -178 C-99 -65 -102 71 -77 161 M17 -178 C99 -65 102 71 77 161" fill="none" stroke="#ae8451" stroke-width="2.5" opacity=".55"/>
<path d="M-52 -5 Q0 6 52 -5 M-55 65 Q0 76 55 65" fill="none" stroke="#debd84" stroke-width="8"/>
</g>''')
# 뒤집은 선체: 독립적인 좌표/색, 한쪽 그림자, 용골, 양쪽 판재선.
boats=[(297,325,-13,1.05,'#ece4ca','#c8ba99'),(580,340,8,1.0,'#bc523a','#923e31'),(814,298,-9,.83,'#e9dec0','#beac86'),(413,755,17,.94,'#3d777c','#285960')]
for x,y,a,scale,c,shade in boats:
    s.append(f'<g transform="translate({x} {y}) rotate({a}) scale({scale})">')
    hull='M0 -190 C-83 -123 -103 35 -63 167 Q0 189 63 167 C103 35 83 -123 0 -190 Z'
    s.append(f'<path d="{hull}" transform="translate(31 23)" fill="#8b704e" opacity=".48"/>')
    # 받침
    s.append('<path d="M-102 -78 L100 -78 M-106 111 L104 111" stroke="#705b42" stroke-width="13"/>')
    s.append(f'<path d="{hull}" fill="{c}"/>')
    s.append(f'<path d="M0 -190 C83 -123 103 35 63 167 Q32 180 0 180 Z" fill="{shade}"/>')
    for side in (-1,1):
        for w in (23,48,68):
            s.append(f'<path d="M0 -177 C{side*w} -85 {side*(w+20)} 37 {side*w*.8} 163" stroke="#f3eddb" stroke-opacity=".34" stroke-width="2" fill="none"/>')
    s.append('<path d="M0 -182 C-4 -64 3 89 0 174" fill="none" stroke="#f6edd6" stroke-width="7"/>')
    s.append('<path d="M-60 159 Q0 179 60 159" fill="none" stroke="#1f3e47" stroke-opacity=".35" stroke-width="5"/>')
    s.append('</g>')
# 두 노: 꼭 같은 길이가 아니다.
s.append('''<g transform="translate(685 764) rotate(-17)">
<path d="M-8 -125 L-8 83" stroke="#665b45" stroke-width="7"/>
<path d="M-8 51 Q-30 99 -16 138 Q-7 147 1 136 L8 67 Z" fill="#eee2bf"/>
<path d="M27 -108 L27 91" stroke="#665b45" stroke-width="7"/>
<path d="M27 63 Q7 101 17 145 Q27 153 37 143 L43 77 Z" fill="#b8583d"/>
</g>
<ellipse cx="666" cy="569" rx="28" ry="21" fill="#927247" opacity=".5"/>
<circle cx="652" cy="557" r="23" fill="#e8dfbf"/>
<circle cx="652" cy="557" r="16" fill="#234c60"/>
<path d="M632 550 Q647 526 670 550" fill="none" stroke="#b5aa8c" stroke-width="3"/>
</g>
<path d="M70 1040 H133" stroke="#bc523a" stroke-width="3"/>
<circle cx="1368" cy="1040" r="4" fill="#244d64"/>
</svg>''')
(ROOT/'An-Afternoon-Ashore.svg').write_text('\n'.join(s)+'\n',encoding='utf-8')
