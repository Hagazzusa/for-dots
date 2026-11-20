"""파일과 PDF 실척을 읽기 전용 검사한다. 실제 프린터·재단 검사를 대신하지 않는다."""
from pathlib import Path
import json,hashlib,sys
import pdfplumber
from PIL import Image
ROOT=Path(__file__).resolve().parent
pt=72/25.4
with pdfplumber.open(ROOT/'output/The-Other-Shoe-Parts.pdf') as doc:
 assert len(doc.pages)==3
 for page in doc.pages:
  assert abs(page.width/pt-210)<.001 and abs(page.height/pt-297)<.001
  bars=[l for l in page.lines if abs(l['x0']/pt-20)<.001 and abs(l['x1']/pt-70)<.001 and abs(l['y0']/pt-15)<.001 and abs(l['y1']/pt-15)<.001]
  assert len(bars)==1
  for ch in page.chars:assert 8*pt<ch['x0']<ch['x1']<202*pt and 8*pt<ch['top']<ch['bottom']<289*pt
 windows=[r for r in doc.pages[0].rects if abs(r['width']/pt-40)<.001 and abs(r['height']/pt-56)<.001];assert len(windows)==2
 sizes=[(round(r['width']/pt,2),round(r['height']/pt,2)) for r in doc.pages[2].rects]
 assert sizes.count((140,80))==1 and sizes.count((80,118))==2
for name,size in [('left.png',(1200,1200)),('right.png',(1200,1200)),('assembled.png',(1600,1400))]:
 im=Image.open(ROOT/'output'/name);im.load();assert im.size==size
if (ROOT/'manifest.json').exists():
 for f,r in json.loads((ROOT/'manifest.json').read_text())['files'].items():
  p=ROOT/f;assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],f
print(json.dumps({'pdf_pages':3,'page_mm':[210,297],'scale_bars_mm':[50,50,50],'windows_mm':[40,56],'base_mm':[140,80],'side_panels_mm':[80,118],'native_pngs_decoded':3,'physical_print_tested':False},ensure_ascii=False))
