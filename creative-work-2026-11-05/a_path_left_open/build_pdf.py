from pathlib import Path
import json,hashlib
from fontTools.ttLib import TTFont as FTFont
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
P=Path(__file__).resolve().parent
DATA=json.loads((P/'search.json').read_text());SHAPES=DATA['shapes']
PUZZLES=[{'name':'가운데를 지나가기','clues':[[2,2]],'count':4},{'name':'두 점을 지나가기','clues':[[1,0],[1,2]],'count':1}]
for p in PUZZLES:
 matches=[s for s in DATA['solutions'] if all(c in s['path'] for c in p['clues'])];assert len(matches)==p['count'];p['answer']=matches[0]
(P/'puzzles.json').write_text(json.dumps(PUZZLES,ensure_ascii=False,indent=2)+'\n')
STRINGS=['길을 남기는 일','네 조각을 놓고 빈칸으로 길을 만드는 종이 퍼즐','판을 채우는 대신 길을 남겨 보세요.',
'1 네 조각을 모두 판의 칸에 맞춰 놓습니다.','2 겹치거나 판 밖으로 나가면 안 됩니다.','3 조각은 90도씩 돌리거나 뒤집어도 됩니다.','4 출발과 도착, 작은 점이 있는 칸은 비워 둡니다.','5 남은 아홉 칸을 가로·세로로 이어 출발에서 도착까지 길을 만듭니다.',
'대각선으로만 닿는 칸은 연결로 세지 않습니다.','조각은 바깥 실선만 오리세요. 안쪽 점선은 자르지 않습니다.','뒤집어서 뒷면이 보여도 괜찮습니다. 색은 규칙이 아닙니다.',
'단면으로 100%(실제 크기) 인쇄하고, 아래 선이 50mm인지 확인하세요.','50mm','두 개의 마당','같은 조각 한 세트를 두 판에 번갈아 사용하세요.','출발','도착','가운데를 지나가기','두 점을 지나가기','길을 남기는 일 해답','먼저 풀어 본 뒤에 펼쳐 보세요.','네 가지 배치 중 하나','두 점을 지나는 유일한 배치','조각을 뒤집는 것도 허용한 기준입니다.','A 3칸','B 3칸','C 5칸','D 5칸','0123456789 ABCD /']
STRINGS.append('다음 쪽에 두 문제의 배치가 있습니다.')
text=''.join(STRINGS)
f=FTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',fontNumber=1);ss=subset.Subsetter();ss.populate(text=text);ss.subset(f);order=f.getGlyphOrder();gs=f.getGlyphSet();glyphs={}
for n in order:
 pen=TTGlyphPen(None);gs[n].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[n]=pen.glyph()
fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
fb.setupNameTable({'familyName':'PathPuzzleSubset','styleName':'Regular','uniqueFontIdentifier':'PathPuzzleSubset','fullName':'PathPuzzleSubset','psName':'PathPuzzleSubset','copyright':'Noto Sans CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.'});fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
font=P/'tmp/pdfs/subset.ttf';fb.save(font);pdfmetrics.registerFont(TTFont('Book',str(font)))
W,H=210*mm,297*mm;CELL=18*mm
COLORS={'A':'#cd836d','B':'#d8b86a','C':'#81aba0','D':'#91a7bd'};INK='#25322f';LIGHT='#9ca9a1'
def new(name,title):
 c=canvas.Canvas(str(P/'output/pdf'/name),pagesize=(W,H),pageCompression=1,invariant=1);c.setTitle(title);c.setAuthor('닷돌이');c.setSubject('네 개의 폴리오미노 조각으로 빈칸의 길을 만드는 종이 퍼즐');return c
def txt(c,s,x,y,size=10,color=INK,center=False):
 c.setFillColor(HexColor(color));c.setFont('Book',size);(c.drawCentredString if center else c.drawString)(x*mm,H-y*mm,s)
def line(c,x1,y1,x2,y2,width=.6,color=INK):
 c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.line(x1*mm,H-y1*mm,x2*mm,H-y2*mm)
def boundary(cells):
 edges=set()
 for x,y in cells:
  for a,b in [((x,y),(x+1,y)),((x+1,y),(x+1,y+1)),((x+1,y+1),(x,y+1)),((x,y+1),(x,y))]:
   if (b,a) in edges:edges.remove((b,a))
   else:edges.add((a,b))
 start=min(a for a,b in edges);current=start;points=[start]
 while True:
  nextpoint=next(b for a,b in edges if a==current);points.append(nextpoint);edges.remove((current,nextpoint));current=nextpoint
  if current==start:break
 assert not edges
 return points
def shape(c,name,cells,x,y,cutout=False,labels=False):
 c.setFillColor(HexColor(COLORS[name]))
 for gx,gy in cells:c.rect(x*mm+gx*CELL,H-y*mm-(gy+1)*CELL,CELL,CELL,stroke=0,fill=1)
 if cutout:
  c.saveState();c.setDash(1.4,2.2);c.setStrokeColor(HexColor('#455750'));c.setLineWidth(.45)
  for gx,gy in cells:c.rect(x*mm+gx*CELL,H-y*mm-(gy+1)*CELL,CELL,CELL,stroke=1,fill=0)
  c.restoreState()
 pts=boundary([tuple(v) for v in cells]);q=c.beginPath();q.moveTo(x*mm+pts[0][0]*CELL,H-y*mm-pts[0][1]*CELL)
 for gx,gy in pts[1:]:q.lineTo(x*mm+gx*CELL,H-y*mm-gy*CELL)
 q.close();c.setStrokeColor(HexColor(INK));c.setLineWidth(1 if cutout else .7);c.drawPath(q,stroke=1,fill=0)
 for gx,gy in (cells if labels else cells[:1]):txt(c,name,x+gx*18+9,y+gy*18+10.7,10,color=INK,center=True)
def board(c,p,x,y,answer=False):
 if answer:
  for name,cells in p['answer']['pieces'].items():shape(c,name,cells,x,y,labels=True)
 # The empty squares, including both ends and every waypoint, stay visibly open.
 for row in range(6):line(c,x,y+18*row,x+90,y+18*row,.5,LIGHT)
 for col in range(6):line(c,x+18*col,y,x+18*col,y+90,.5,LIGHT)
 c.setStrokeColor(HexColor(INK));c.setLineWidth(.9);c.rect(x*mm,H-(y+90)*mm,90*mm,90*mm,stroke=1,fill=0)
 if answer:
  pts=p['answer']['path'];c.setStrokeColor(HexColor('#758c80'));c.setLineWidth(1.1);q=c.beginPath();q.moveTo((x+pts[0][0]*18+9)*mm,H-(y+pts[0][1]*18+9)*mm)
  for gx,gy in pts[1:]:q.lineTo((x+gx*18+9)*mm,H-(y+gy*18+9)*mm)
  c.drawPath(q)
 for gx,gy,label in [(0,0,'출발'),(4,4,'도착')]:
  c.setFillColor(HexColor('#ffffff'));c.rect((x+gx*18+2)*mm,H-(y+gy*18+12)*mm,14*mm,6*mm,stroke=0,fill=1)
  txt(c,label,x+gx*18+9,y+gy*18+10.7,9,center=True)
 for gx,gy in p['clues']:
  c.setFillColor(HexColor('#c49a3e'));c.setStrokeColor(HexColor(INK));c.setLineWidth(.6);c.circle((x+gx*18+9)*mm,H-(y+gy*18+9)*mm,2*mm,stroke=1,fill=1)
def footer(c,page):txt(c,f'길을 남기는 일   {page}',105,290,7,color='#6c7871',center=True)
main=new('A-Path-Left-Open.pdf','길을 남기는 일')
txt(main,'길을 남기는 일',18,25,26);txt(main,STRINGS[1],18,36,10.5)
for i,s in enumerate(STRINGS[3:8]):txt(main,s,18,53+i*8,10.2)
txt(main,STRINGS[8],23,91,9.2)
txt(main,STRINGS[9],18,107,9.2);txt(main,STRINGS[10],18,114,9.2)
for name,x,y in [('A',32,135),('B',123,135),('C',32,199),('D',123,199)]:
 txt(main,f'{name} {len(SHAPES[name])}칸',x,y-7,10);shape(main,name,SHAPES[name],x,y,cutout=True)
txt(main,STRINGS[11],18,266,8.5)
line(main,18,276,68,276,1);line(main,18,273.5,18,278.5,1);line(main,68,273.5,68,278.5,1);txt(main,'50mm',43,272,8,center=True)
footer(main,1);main.showPage()
txt(main,'두 개의 마당',18,25,24);txt(main,STRINGS[14],18,39,10)
for i,(p,y) in enumerate(zip(PUZZLES,[68,192])):
 txt(main,f'{i+1} {p["name"]}',60,y-8,11);board(main,p,60,y)
footer(main,2);main.showPage();main.save()
answers=new('A-Path-Left-Open-Answers.pdf','길을 남기는 일 해답')
txt(answers,'길을 남기는 일 해답',105,95,24,center=True)
txt(answers,'다음 쪽에 두 문제의 배치가 있습니다.',105,112,11,center=True)
txt(answers,'먼저 풀어 본 뒤에 펼쳐 보세요.',105,123,10,center=True)
footer(answers,1);answers.showPage()
txt(answers,'길을 남기는 일 해답',18,25,24);txt(answers,'조각을 뒤집는 것도 허용한 기준입니다.',18,39,10)
for i,(p,y) in enumerate(zip(PUZZLES,[68,192])):
 label='네 가지 배치 중 하나' if i==0 else '두 점을 지나는 유일한 배치'
 txt(answers,f'{i+1} {label}',60,y-8,11);board(answers,p,60,y,answer=True)
footer(answers,2);answers.showPage();answers.save()
(P/'print-geometry.json').write_text(json.dumps({'page_mm':[210,297],'cell_mm':18,'board_mm':90,'scale_bar_mm':50,'main_pages':2,'answer_pages':2,'boards':[{'x_mm':60,'y_mm':y,'clues':p['clues']} for p,y in zip(PUZZLES,[68,192])],'piece_areas':{n:len(v) for n,v in SHAPES.items()},'printed_outlines':{n:boundary([tuple(c) for c in v]) for n,v in SHAPES.items()}},ensure_ascii=False,indent=2)+'\n')
print('Built puzzle and separate answer PDFs.')
