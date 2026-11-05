"""드로잉 파일과 좌표 보존 검사. 기본 실행은 읽기 전용입니다."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent

def verify():
 d=json.loads((P/'output/net/model.json').read_text());p=np.array(d['after']);edges=np.delete(np.array(d['edges']),d['cut_edge_index'],axis=0);rest=np.delete(np.array(d['rest_lengths']),d['cut_edge_index'])
 result=[];all_paths=[]
 for name,view,size in [('near','0.27 0.17 1.0 1.08',(900,1050)),('fragment','0.35 0.10 .76 .63',(912,756))]:
  tree=ET.parse(P/f'output/ink-study/{name}.svg');root=tree.getroot();assert root.attrib['viewBox']==view
  paths=root.findall('.//{http://www.w3.org/2000/svg}path');assert len(paths)==143
  curves=0
  for node,(a,b),r in zip(paths,edges,rest):
   coords=np.array([float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',node.attrib['d'])])
   assert np.array_equal(coords[:2],p[a]) and np.array_equal(coords[-2:],p[b])
   length=np.linalg.norm(p[b]-p[a]);slack=r-length
   if slack>1e-6:
    curves+=1;assert 'Q' in node.attrib['d']
    expected=(p[a]+p[b])/2+[0,np.sqrt(6*length*slack)/2]
    assert np.array_equal(coords[2:4],expected)
   else:assert 'L' in node.attrib['d']
   assert .0012<=float(node.attrib['stroke-width'])<=.0027
  assert curves==4
  with Image.open(P/f'output/ink-study/{name}.png') as im:im.load();assert im.size==size
  all_paths.append([x.attrib for x in paths]);result.append({'그림':name,'선 수':143,'해석적 곡선 수':curves,'화면 크기':list(size)})
 assert all_paths[0]==all_paths[1]
 return {'검사':result,'두 크롭의 같은 경로·선 굵기':True,'선 끝 좌표의 수치 망 일치':True,'한계':'곡선은 드로잉 해석이며 길이 보존·현수선·힘 평형 검사가 아닙니다. 크롭의 조형적 성취는 자동 판정하지 않습니다.'}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
