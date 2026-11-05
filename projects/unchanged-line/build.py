from pathlib import Path
import json, hashlib
from fontTools.ttLib import TTFont as FTFont
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
P=Path(__file__).resolve().parent
W,H=480,600
LINE=[(90,300),(170,300),(210,345),(270,345),(310,300),(390,300)]
PAPER='#f6f2e9'; CONTEXT='#a4aaa5'; LIGHT='#dedfd6'; INK='#333c38'; RUST='#a54e39'
CAPTIONS=[['먼저 한 줄.'],[],[],[],['나머지를 지웠다.']]
title='한 줄의 바깥'
alltext=title+'0123456789 / .'+''.join(sum(CAPTIONS,[]))
f=FTFont('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',fontNumber=1)
s=subset.Subsetter();s.populate(text=alltext);s.subset(f)
order=f.getGlyphOrder();gs=f.getGlyphSet();glyphs={}
for n in order:
 pen=TTGlyphPen(None);gs[n].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[n]=pen.glyph()
fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
fb.setupNameTable({'familyName':'UnchangedLineSubset','styleName':'Regular','uniqueFontIdentifier':'UnchangedLineSubset-Regular','fullName':'UnchangedLineSubset Regular','psName':'UnchangedLineSubset-Regular','copyright':'Noto Serif CJK, SIL Open Font License 1.1. Converted subset for document embedding.'})
fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
font=P/'tmp/pdfs/subset.ttf';fb.save(font);pdfmetrics.registerFont(TTFont('Book',str(font)))
c=canvas.Canvas(str(P/'output/pdf/Outside-One-Line.pdf'),pagesize=(W,H),pageCompression=1,invariant=1)
c.setTitle(title);c.setAuthor('dot');c.setSubject('같은 선을 다섯 번 보는 작은 벡터 그림책')
def stroke(points,color=CONTEXT,width=.8):
 c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setLineCap(1);c.setLineJoin(1)
 q=c.beginPath();q.moveTo(*points[0])
 for point in points[1:]:q.lineTo(*point)
 c.drawPath(q)
def polygon(points,fill):
 c.setFillColor(HexColor(fill));q=c.beginPath();q.moveTo(*points[0])
 for point in points[1:]:q.lineTo(*point)
 q.close();c.drawPath(q,stroke=0,fill=1)
def text(s,x,y,size=12,center=False,color=INK):
 c.setFont('Book',size);c.setFillColor(HexColor(color));(c.drawCentredString if center else c.drawString)(x,y,s)
def circle(x,y,r=4):
 c.setFillColor(HexColor(PAPER));c.setStrokeColor(HexColor(CONTEXT));c.setLineWidth(.8);c.circle(x,y,r,stroke=1,fill=1)
for i in range(5):
 c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,stroke=0,fill=1)
 if i in [0,4]:text(title,240,518,13,center=True)
 if i==1:
  # Elevation, not a physical construction diagram.
  polygon([(110,300),(170,300),(210,345),(270,345),(310,300),(370,300),(370,222),(110,222)],'#eceae0')
  stroke([(110,300),(110,222),(370,222),(370,300)])
  stroke([(80,222),(400,222)],width=.65)
  stroke([(220,222),(220,271),(253,271),(253,222)])
  stroke([(145,256),(183,256),(183,280),(145,280),(145,256)])
  stroke([(164,256),(164,280)],width=.5)
  stroke([(294,256),(332,256),(332,280),(294,280),(294,256)])
  stroke([(313,256),(313,280)],width=.5)
 elif i==2:
  # Transit diagram: neighboring routes confer a network on the fixed line.
  stroke([(65,391),(130,391),(170,351),(170,300),(170,237),(213,194)],width=1.1)
  stroke([(270,410),(270,345),(320,395),(407,395)],width=1.1)
  stroke([(90,211),(125,246),(310,246),(310,300),(362,352),(410,352)],width=1.1)
  for x,y in [(65,391),(130,391),(170,300),(170,237),(213,194),(270,410),(270,345),(320,395),(407,395),(90,211),(310,246),(310,300),(410,352),(90,300),(390,300)]:circle(x,y,3.8)
 elif i==3:
  # A deliberately unitless invented graph, not measured real-world data.
  for y in [255,300,345,390]:stroke([(77,y),(401,y)],color=LIGHT,width=.6)
  for x in [90,150,210,270,330,390]:stroke([(x,237),(x,402)],color=LIGHT,width=.5)
  stroke([(77,408),(77,237),(405,237)])
  for label,y in [('0',255),('1',300),('2',345),('3',390)]:text(label,62,y-3,8,color='#737d76')
  for label,x in [('0',90),('1',150),('2',210),('3',270),('4',330),('5',390)]:text(label,x,221,8,center=True,color='#737d76')
 # Identical unobscured target path; drawn last in every context.
 stroke(LINE,RUST,2.2)
 for j,line in enumerate(CAPTIONS[i]):text(line,240,141-j*22,12,center=True)
 text(str(i+1),240,42,8,center=True,color='#737d76')
 c.showPage()
c.save()
(P/'design.json').write_text(json.dumps({'title':title,'pages':5,'page_points':[W,H],'target_line':LINE,'target_width':2.2,'target_color':RUST,'captions':CAPTIONS,'contexts':['bare','house elevation','fictional transit diagram','unitless invented graph','bare']},ensure_ascii=False,indent=2)+'\n')
print('Built five-page vector artist book.')
