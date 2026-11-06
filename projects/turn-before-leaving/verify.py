"""풀이·도달 상태 전이·PDF 경계·매니페스트의 읽기 전용 검사."""
from pathlib import Path
from collections import deque,defaultdict
import json,hashlib,re,sys
sys.dont_write_bytecode=True
import pdfplumber
from pypdf import PdfReader
from solve import solve,transitions
from independent_check import successors
P=Path(__file__).resolve().parent
ps=json.loads((P/'puzzles.json').read_text());saved=json.loads((P/'solutions.json').read_text());report={'문제':[],'PDF':[]}
for p in ps:
 s=solve(p);assert s==saved[p['id']]
 start=(p['start'],tuple(p['arrows']),0);seen={start};q=deque([start]);edges=0
 while q:
  st=q.popleft();a=[] if st[0]==p['goal'] else list(transitions(st,p['budget']));b=successors(st,goal=p['goal'],budget=p['budget']);assert a==b,(st,a,b)
  edges+=len(a)
  for _,target in a:
   if target not in seen:seen.add(target);q.append(target)
 report['문제'].append({'번호':p['id'],'최단 이동':s['minimum_moves'],'최단 선택열':s['shortest_solutions'],'도달 상태':len(seen),'대조한 전이':edges})
for stem,pages in [('Before-You-Leave',4),('Before-You-Leave-Solutions',3)]:
 file=P/'output/pdf'/f'{stem}.pdf';reader=PdfReader(file);assert len(reader.pages)==pages
 with pdfplumber.open(file) as pdf:
  total=0
  for pi,page in enumerate(pdf.pages,1):
   assert abs(page.width-595.28)<.01 and abs(page.height-841.89)<.01
   rows=defaultdict(list)
   for c in page.chars:
    assert c['text'] not in ('\ufffd','\x00')
    assert 40<=c['x0']<=c['x1']<=555.28,(pi,c)
    assert 35<=c['top']<c['bottom']<=822,(pi,c)
    assert 'ArrowPuzzleNotoSerifKR' in c['fontname']
    rows[round(c['top'],2)].append(c);total+=1
   for row in rows.values():
    row.sort(key=lambda c:c['x0'])
    assert all(a['x1']<=b['x0']+.1 for a,b in zip(row,row[1:])),(stem,pi)
   assert page.extract_text().rstrip().endswith(str(pi))
  if stem.endswith('Solutions'):
   txt=''.join(p.extract_text() for p in pdf.pages)
   for n in [4,8,12]:assert f'최단 {n}번 이동' in txt
   for n in [2,5]:assert f'회전 {n}번' in txt
 for page in reader.pages:
  for ref in page['/Resources']['/Font'].get_object().values():
   f=ref.get_object()
   if 'ArrowPuzzle' in str(f.get('/BaseFont','')):
    desc=f['/FontDescriptor'].get_object();assert '/FontFile2' in desc and '/ToUnicode' in f
 report['PDF'].append({'파일':file.name,'쪽 수':pages,'검사한 글자':total,'글꼴 내장':True,'본문 경계':True})
manifest=P/'manifest.json'
if manifest.exists():
 for f in json.loads(manifest.read_text())['files']:
  b=(P/f['path']).read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print(json.dumps(report,ensure_ascii=False,indent=2))
