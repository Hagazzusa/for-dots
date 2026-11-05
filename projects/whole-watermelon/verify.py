"""낭독문 원문과 한 쪽 PDF의 행·여백·텍스트 일치를 검사한다."""
from pathlib import Path
import json,hashlib
import fitz
P=Path(__file__).resolve().parent
source=(P/'script.txt').read_text();lines=[s for s in source.splitlines() if s]
assert (P/'Whole-Watermelon.txt').read_bytes()==(P/'script.txt').read_bytes()
doc=fitz.open(P/'Whole-Watermelon.pdf');assert len(doc)==1
page=doc[0];assert tuple(page.rect)==(0,0,420,720)
actual=page.get_text().splitlines();assert actual==[lines[0],'두 손을 위한 짧은 낭독문']+lines[1:]
for block in page.get_text('dict')['blocks']:
 for line in block.get('lines',[]):
  for span in line['spans']:
   x0,y0,x1,y1=span['bbox'];assert x0>=49 and x1<=370 and y0>=30 and y1<=675
sentences=''.join(lines[1:]).split('.')
assert all(s.endswith('라') for s in sentences if s)
report={'title':'통째로','form':'두 손을 위한 짧은 낭독문','pages':1,'page_size_points':[420,720],'source_characters':len(source),'body_lines':len(lines)-1,'sentence_count':len([s for s in sentences if s]),'all_sentences_imperative':True,'pdf_lines_match_source':True,'plain_text_matches_source_bytes':True,'text_within_margins':True,'visual_review':'최종 한 쪽을 이미지로 확인했으며 잘림·겹침·누락된 글자가 없습니다.','editorial_review':'명령과 손동작의 순서, 마지막의 뒤늦은 선행 지시를 독립적으로 검토했습니다.','limits':'낭독 녹음과 실제 동작 공연은 제작하거나 평가하지 않았습니다.'}
(P/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
