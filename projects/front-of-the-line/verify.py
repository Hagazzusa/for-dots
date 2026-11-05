from pathlib import Path
import json,hashlib,re
import fitz
P=Path(__file__).resolve().parent
pdf=P/'output/pdf/Front-of-the-Line.pdf';txt=P/'output/text/Front-of-the-Line.txt';source=(P/'story.txt').read_text()
assert txt.read_text()==source
doc=fitz.open(pdf);assert len(doc)==6
extracted=[];pages=[]
for i,page in enumerate(doc):
 assert tuple(page.rect)==(0,0,480,680)
 body=[]
 for block in page.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   if not (line['bbox'][1]>35 and line['bbox'][3]<640):continue
   text=''.join(span['text'] for span in line['spans'])
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox'];assert x0>=47 and x1<=433 and y0>=44 and y1<640,(i,span)
   body.append(text)
 extracted.extend(body);pages.append({'page':i+1,'body_lines':len(body),'last_line':body[-1]})
norm=lambda s:re.sub(r'\s+','',s)
assert norm(''.join(extracted))==norm(source),'PDF text differs from source'
assert min(p['body_lines'] for p in pages)>=20
q={'title':'맨 앞','pages':len(doc),'page_size_points':[480,680],'source_characters':len(source),'source_nonempty_lines':len([l for l in source.splitlines() if l]),'pdf_text_matches_source_ignoring_whitespace':True,'plain_text_matches_source_bytes':txt.read_bytes()==(P/'story.txt').read_bytes(),'all_body_text_within_margins':True,'page_lines':pages,'visual_review':'Pending final rendered-page inspection.','editorial_review':'Timeline, cast counts, door movements, props, queue order and ending reviewed; continuity corrections incorporated.','fiction':True,'hashes':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [pdf,txt]}}
(P/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False,indent=2))
