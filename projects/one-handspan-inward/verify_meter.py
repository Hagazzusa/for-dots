#!/usr/bin/env python3
"""편집 원문과 정한 음보의 일치, 한글 표기 음절 수를 읽기 전용으로 확인한다."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def verify():
 m=json.loads((ROOT/'meter.json').read_text(encoding='utf-8'));lines=(ROOT/'poem.txt').read_text(encoding='utf-8').splitlines()
 assert lines[:3]==[m['제목'],'시조',''] and len(lines[3:])==3
 assert len(m['장'])==3 and all(len(x)==4 for x in m['장'])
 counts=[]
 for line,feet in zip(lines[3:],m['장']):
  assert ''.join(line.split())==''.join(''.join(feet).split())
  row=[]
  for foot in feet:
   syllables=''.join(foot.split());assert all('가'<=c<='힣' for c in syllables);row.append(len(syllables))
  counts.append(row)
 assert counts==m['음절 수'] and counts[2][0]==3
 return {'장':3,'음보':12,'장별 음절 수':counts,'전체 표기 음절 수':sum(map(sum,counts)),'원문과 음보 일치':True,'한계':m['한계']}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
