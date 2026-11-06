"""시의 행·연·글꼴·조판 경계와 보존 파일을 읽기 전용으로 확인한다."""
from pathlib import Path
import hashlib,json,re
from collections import defaultdict
import pdfplumber
from pypdf import PdfReader
p=Path(__file__).resolve().parent
raw=(p/'poem.txt').read_bytes();source=raw.decode('utf-8');lines=source.splitlines();body=lines[2:]
assert len([x for x in body if x])==14
assert len('\n'.join(body).strip().split('\n\n'))==4
assert (p/'output/text/Water-in-One-Ear.txt').read_bytes()==raw
pdf=p/'output/pdf/Water-in-One-Ear.pdf';reader=PdfReader(pdf);assert len(reader.pages)==1;assert reader.metadata.title==lines[0]
with pdfplumber.open(pdf) as d:
 page=d.pages[0];assert (page.width,page.height)==(480,680);rows=defaultdict(list)
 for c in page.chars:
  assert c['text'] not in ('\ufffd','\x00');assert 71.9<=c['x0']<=c['x1']<=408
  assert 60<=c['top']<c['bottom']<580;assert 'WaterInOneEarNotoSerifKR' in c['fontname']
  rows[round(c['top'],3)].append(c)
 actual=[];prevbottom=0
 for top,chars in sorted(rows.items()):
  chars.sort(key=lambda c:c['x0']);assert top>prevbottom;prevbottom=max(c['bottom'] for c in chars)
  assert all(a['x1']<=b['x0']+.1 for a,b in zip(chars,chars[1:]))
  actual.append(''.join(c['text'] for c in chars))
 clean=lambda s:re.sub(r'\s+','',s)
 assert [clean(s) for s in actual]==[clean(s) for s in lines if s]
 tops=sorted(rows)[1:];gaps=[round(b-a,3) for a,b in zip(tops,tops[1:])]
 assert gaps.count(39)==3 and gaps.count(24)==10
for ref in reader.pages[0]['/Resources']['/Font'].get_object().values():
 f=ref.get_object()
 if 'WaterInOneEar' in str(f.get('/BaseFont','')):assert '/FontFile2' in f['/FontDescriptor'].get_object() and '/ToUnicode' in f
if (p/'manifest.json').exists():
 for f in json.loads((p/'manifest.json').read_text())['files']:
  b=(p/f['path']).read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print(json.dumps({'제목':lines[0],'시 행 수':14,'연 수':4,'PDF 쪽 수':1,'PDF 원문 행별 글자 일치':True,'TXT 원문 바이트 일치':True,'연 간격 보존':True,'글꼴 내장·경계·겹침 검사':True},ensure_ascii=False,indent=2))
