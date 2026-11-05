#!/usr/bin/env python3
"""악보의 시간 배분·방향·끝점을 검사한다. 음향이나 신체 동작의 검사가 아니다."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def verify():
 data=json.loads((ROOT/'score.json').read_text());phrases=data['phrases'];length=data['line_length_mm'];beats=data['beats_per_phrase']
 assert length==60 and beats==8 and len(phrases)==6
 moves=[p['move_beats'] for p in phrases];holds=[p['hold_beats'] for p in phrases]
 assert moves==[6,4,2,2,4,6] and holds==[2,4,6,6,4,2]
 assert all(a+b==beats for a,b in zip(moves,holds))
 position=0;timeline=[{'박':0,'위치_mm':0}];elapsed=0;distance=0
 for i,p in enumerate(phrases):
  assert p['number']==i+1 and p['direction']==('오른쪽' if i%2==0 else '왼쪽')
  target=length if i%2==0 else 0;start=position
  for local_beat in range(1,beats+1):
   x=start+(target-start)*min(local_beat/p['move_beats'],1)
   assert 0<=x<=length
   timeline.append({'박':elapsed+local_beat,'위치_mm':x})
  distance+=abs(target-start);position=target;elapsed+=beats
 assert position==0 and elapsed==48 and sum(moves)==sum(holds)==24
 return {'제목':data['title'],'편도 이동':6,'왕복':3,'총 박':elapsed,'이동 박':sum(moves),'머무는 박':sum(holds),'한 획 길이_mm':length,'직선 경로 기준 총 이동 거리_mm':distance,'마지막 위치_mm':position,'한계':'이 시간표는 지시한 동작의 일관성 검사입니다. 실제 연주 시간·마찰음·손의 편안함을 측정한 결과가 아닙니다.','박 경계 위치':timeline}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
