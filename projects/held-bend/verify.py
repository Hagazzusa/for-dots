#!/usr/bin/env python3
"""보류 연구의 출력 구조와 여백을 읽기 전용으로 검사한다."""
from pathlib import Path
import xml.etree.ElementTree as ET
import math,json
from PIL import Image
P=Path(__file__).resolve().parent
ns={'s':'http://www.w3.org/2000/svg'}
results=[]
for v in (1,2,3):
 root=ET.parse(P/f'output/variant-{v}.svg').getroot()
 polygons=root.findall('s:polygon',ns);paths=root.findall('s:path',ns)
 assert len(polygons)==720 and len(paths)==4320
 coords=[tuple(map(float,pair.split(','))) for poly in polygons for pair in poly.get('points').split()]
 assert all(math.isfinite(a) and math.isfinite(b) and 15<a<885 and 15<b<885 for a,b in coords)
 assert not any('href' in k for el in root.iter() for k in el.attrib)
 results.append({'변형':v,'면':len(polygons),'결선 조각':len(paths),'가장자리 최소 여백':round(min(min(x,y,900-x,900-y) for x,y in coords),3)})
with Image.open(P/'output/comparison.png') as im:assert im.size==(1500,500) and im.mode=='RGB'
print(json.dumps({'변형 검사':results,'외부 의존성 없음':True,'비교판 크기':[1500,500],'한계':'화면 좌표와 파일 구조 검사이며 물리·연속 자기 교차 검사가 아닙니다.'},ensure_ascii=False,indent=2))
