from pathlib import Path
from fontTools.ttLib import TTFont as FTFont
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape
P=Path(__file__).resolve().parent
source=(P/'script.txt').read_text();alltext=source+'통째로두 손을 위한 짧은 낭독문'
f=FTFont('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',fontNumber=1);ss=subset.Subsetter();ss.populate(text=alltext);ss.subset(f);order=f.getGlyphOrder();gs=f.getGlyphSet();glyphs={}
for n in order:
 pen=TTGlyphPen(None);gs[n].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[n]=pen.glyph()
fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
fb.setupNameTable({'familyName':'WatermelonReading','styleName':'Regular','uniqueFontIdentifier':'WatermelonReading','fullName':'WatermelonReading','psName':'WatermelonReading','copyright':'Noto CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.'})
fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
dest=P/'tmp/pdfs/WatermelonReading.ttf';dest.parent.mkdir(parents=True,exist_ok=True);fb.save(dest);pdfmetrics.registerFont(TTFont('WatermelonReading',str(dest)))

# 행과 빈 연의 간격을 유지하는 한 쪽짜리 낭독판.
from reportlab.pdfgen.canvas import Canvas
W,H=420,720
out=P/'Whole-Watermelon.pdf'
c=Canvas(str(out),pagesize=(W,H),pageCompression=1)
c.setTitle('통째로');c.setAuthor('닷돌이');c.setSubject('두 손을 위한 짧은 낭독문')
c.setFillColor(HexColor('#000000'));c.setFont('WatermelonReading',24);c.drawString(50,665,'통째로')
c.setFont('WatermelonReading',9.5);c.drawString(50,641,'두 손을 위한 짧은 낭독문')
c.setFont('WatermelonReading',12.5);y=603
lines=source.splitlines()[2:]
for line in lines:
 if not line:
  y-=8;continue
 assert pdfmetrics.stringWidth(line,'WatermelonReading',12.5)<=W-100
 assert y>=45
 c.drawString(50,y,line);y-=18.5
c.showPage();c.save()
(P/'Whole-Watermelon.txt').write_bytes((P/'script.txt').read_bytes())
print(out)
