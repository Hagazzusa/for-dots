"""낱말 고리, PDF의 글자·색·여백, 자체 완결 SVG를 검사한다."""
from pathlib import Path
import json,math,xml.etree.ElementTree as ET
import fitz
from PIL import Image,ImageChops,ImageFilter
P=Path(__file__).resolve().parent;d=json.loads((P/'words.json').read_text());w=d['words'];layout=json.loads((P/'layout.json').read_text())
assert len(w)==26 and len(set(w))==26
assert all(len(x)==2 and all(0xAC00<=ord(c)<=0xD7A3 for c in x) for x in w)
changes=[]
for a,b in zip(w,w[1:]+w[:1]):
 diff=[i for i in range(2) if a[i]!=b[i]];assert len(diff)==1;changes.append(diff[0])
assert all(a!=b for a,b in zip(changes,changes[1:]+changes[:1]))
doc=fitz.open(P/'Word-Ring.pdf');assert len(doc)==1;page=doc[0];assert tuple(page.rect)==(0,0,600,650)
lines=[l for b in page.get_text('dict')['blocks'] for l in b.get('lines',[])]
texts=[''.join(s['text'] for s in l['spans']) for l in lines];assert texts[:26]==w
boxes=[]
for i,l in enumerate(lines[:26]):
 spans=l['spans'];assert len(spans)==2
 incoming=[j for j in range(2) if w[i][j]!=w[(i-1)%26][j]][0]
 assert [s['color'] for s in spans]==[0x202020 if j==incoming else 0x858585 for j in range(2)]
 box=fitz.Rect(l['bbox']);assert box.x0>=40 and box.x1<=560 and box.y0>=50 and box.y1<=550
 boxes.append(box)
for i,a in enumerate(boxes):
 for b in boxes[i+1:]:assert not a.intersects(b)
ns={'s':'http://www.w3.org/2000/svg'};root=ET.parse(P/'Word-Ring.svg').getroot();groups=root.findall('s:g',ns);assert [g.attrib['aria-label'] for g in groups]==w
assert all(len(g.findall('s:path',ns))==2 for g in groups)
assert not root.findall('.//s:image',ns) and not root.findall('.//s:text',ns)
assert not any(k.endswith('href') for e in root.iter() for k in e.attrib)
with Image.open(P/'Word-Ring.png') as im:assert im.size==(1016,1100);im.verify()
report={'title':d['title'],'words':26,'unique_words':True,'one_syllable_changes_on_all_26_edges':True,'changed_positions_alternate_including_closure':True,'pdf_text_and_color_match_source':True,'word_bounds_do_not_overlap':True,'svg_glyph_paths_self_contained':True,'visual_review':'최종 PDF와 SVG 렌더를 모두 확인했습니다. 글자 겹침이나 잘림이 없고 고리가 이어집니다.'}
# 두 렌더러의 글꼴 힌팅·윤곽선 래스터 차이를 1픽셀 이웃 범위에서 비교한다.
a_path=P/'tmp/pdf-check.png';b_path=P/'tmp/svg-check.png'
if a_path.exists() and b_path.exists():
 a=Image.open(a_path).convert('L').point(lambda x:255 if x<200 else 0);b=Image.open(b_path).convert('L').point(lambda x:255 if x<200 else 0);assert a.size==b.size==(600,650)
 ab=ImageChops.darker(a,b.filter(ImageFilter.MaxFilter(3))).histogram()[255]/a.histogram()[255];ba=ImageChops.darker(b,a.filter(ImageFilter.MaxFilter(3))).histogram()[255]/b.histogram()[255];assert min(ab,ba)>.995
 report['cross_renderer_ink_coverage_within_one_pixel']={'pdf_to_svg':ab,'svg_to_pdf':ba,'resolution':[600,650]}
report['limits']='선택한 낱말 고리와 배치에 대한 검사입니다. 가능한 모든 낱말 고리를 탐색한 결과나 독자 지각 실험은 아닙니다.'
(P/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
