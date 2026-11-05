from pathlib import Path
from pypdf import PdfReader
import fitz,re,json,hashlib
P=Path(__file__).resolve().parent
f=P/'output/pdf/Under-Observation.pdf';reader=PdfReader(f);assert len(reader.pages)==5
plain=''.join(page.extract_text() for page in reader.pages)
norm=lambda x:re.sub(r'\s+','',x)
normed=norm(plain)
lines=[x.strip() for x in (P/'play.txt').read_text().splitlines() if x.strip()]
missing=[line for line in lines if norm(line) not in normed];assert not missing,missing
pdf=fitz.open(f);bad=[]
for i,page in enumerate(pdf):
 for block in page.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if x0<45 or x1>435 or y0<15 or y1>665:bad.append([i+1,span['text'],span['bbox']])
assert not bad,bad
q={'title':'확인 중','pages':5,'page_points':[480,680],'nonempty_source_lines_verified':len(lines),'all_source_lines_present':True,'text_bounds_passed':True,'editorial_review':'Two independent readings; revised fees, afternoon test timing, loan deadline, receipt handling, dialogue repetition and executable stage actions. Final continuity check passed.','visual_review':'Pending latest final render inspection.','limits':['Not rehearsed, staged or timed with performers. No verified runtime is claimed.','Fictional people and transaction; not an appliance diagnosis or repair guide.','Not tagged PDF/UA; plain UTF-8 script retained as an editable reading alternative.'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False))
