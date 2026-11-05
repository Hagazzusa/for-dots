#!/usr/bin/env python3
"""연구 그림과 수치 표본의 파일·좌표·고정점을 읽기 전용 검사한다."""
from pathlib import Path
import argparse,json,re,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def verify():
 out=ROOT/'output';counts={}
 for stem,size in [('study',(900,800)),('cut',(900,650))]:
  for i in range(1,4):
   name=f'{stem}-{i}';tree=ET.parse(out/f'{name}.svg');paths=tree.findall('.//{http://www.w3.org/2000/svg}path');counts[name]=len(paths)
   for p in paths:
    xy=np.array([float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',p.attrib['d'])]).reshape(-1,2)
    assert len(xy)>1 and np.isfinite(xy).all() and (xy>=0).all() and (xy[:,0]<size[0]).all() and (xy[:,1]<size[1]).all()
   with Image.open(out/f'{name}.png') as im:im.load();assert im.size==size
 assert counts['study-1']==46 and counts['study-3']==67 and all(counts[f'cut-{i}']==18 for i in range(1,4))
 with Image.open(out/'comparison.png') as im:im.load();assert im.size==(1800,1100)
 with np.load(out/'cut_motion.npz',allow_pickle=False) as z:
  assert set(z.files)=={'0','120','360','2400'}
  first=z['0'];assert first.shape==(2,21,2)
  for k in z.files:
   a=z[k];assert a.shape==first.shape and np.isfinite(a).all()
   assert np.array_equal(a[0,0],first[0,0]) and np.array_equal(a[1,-1],first[1,-1])
 record=json.loads((out/'cut_check.json').read_text());err=record['max_segment_length_error'];assert 0<=err<.0002
 extra=out/'unequal';ticks=[0,24,48,72,96,144,192,288,384]
 with np.load(extra/'motion.npz',allow_pickle=False) as z:
  assert set(z.files)=={str(t) for t in ticks};first=z['0'];assert first.shape==(2,31,2)
  for tick in ticks:
   a=z[str(tick)];assert a.shape==first.shape and np.isfinite(a).all()
   assert np.array_equal(a[0,0],first[0,0]) and np.array_equal(a[1,-1],first[1,-1])
   paths=ET.parse(extra/f'{tick:03}.svg').findall('.//{http://www.w3.org/2000/svg}path');assert len(paths)==2
   for part,path in zip(a,paths):
    coords=np.array([float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',path.attrib['d'])]).reshape(-1,2)
    expected=part*300+np.array([450,85]);assert np.max(abs(coords-expected))<=.000501
   with Image.open(extra/f'{tick:03}.png') as im:im.load();assert im.size==(900,650)
 with Image.open(extra/'comparison.png') as im:im.load();assert im.size==(1800,1350)
 return {'상태':'보류 연구','추가 연구':{'지지점 높이 차이_m':.32,'표본 수':len(ticks),'시간_s':[t/480 for t in ticks],'SVG와 수치 좌표 일치':True},'SVG 경로 수':counts,'전체 이미지 디코드':True,'수치 표본':4,'고정점 일치':True,'선분 길이 최대 오차_m':err,'한계':'파일과 좌표 검사이며 독립적인 역학 검증은 아닙니다.'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--report',type=Path);a=ap.parse_args();s=json.dumps(verify(),ensure_ascii=False,indent=2)+'\n'
 if a.report:a.report.write_text(s,encoding='utf-8')
 print(s,end='')
if __name__=='__main__':main()
