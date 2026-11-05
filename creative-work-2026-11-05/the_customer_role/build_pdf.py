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
source=(P/'story.txt').read_text();alltext=source+'고객 역할0123456789'
f=FTFont('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',fontNumber=1);ss=subset.Subsetter();ss.populate(text=alltext);ss.subset(f);order=f.getGlyphOrder();gs=f.getGlyphSet();glyphs={}
for n in order:
 pen=TTGlyphPen(None);gs[n].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[n]=pen.glyph()
fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
fb.setupNameTable({'familyName':'CustomerStory','styleName':'Regular','uniqueFontIdentifier':'CustomerStory','fullName':'CustomerStory','psName':'CustomerStory','copyright':'Noto CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.'})
fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
dest=P/'tmp/pdfs/CustomerStory.ttf';fb.save(dest);pdfmetrics.registerFont(TTFont('CustomerStory',str(dest)))
styles={
 'title':ParagraphStyle('Title',fontName='CustomerStory',fontSize=26,leading=34,spaceAfter=9,textColor=HexColor('#000000')),
 'subtitle':ParagraphStyle('Subtitle',fontName='CustomerStory',fontSize=10,leading=17,spaceAfter=24,textColor=HexColor('#000000')),
 'body':ParagraphStyle('Body',fontName='CustomerStory',fontSize=11.5,leading=17.5,firstLineIndent=11.5,spaceAfter=1,wordWrap=None,allowWidows=0,allowOrphans=0,textColor=HexColor('#202020')),
}
W,H=480,680
out=P/'output/pdf/The-Customer-Role.pdf'
doc=SimpleDocTemplate(str(out),pagesize=(W,H),leftMargin=48,rightMargin=48,topMargin=45,bottomMargin=47,title='고객 역할',author='닷돌이',subject='독립적인 짧은 소설',pageCompression=1)
flow=[]
lines=[line for line in source.splitlines() if line]
for i,line in enumerate(lines):
 key='title' if i==0 else 'subtitle' if i==1 else 'body'
 para=Paragraph(escape(line),styles[key])
 if i+1<len(lines) and key=='body':
  nxt=lines[i+1]
  if (line.endswith('말했다.') and nxt.startswith('“')) or (line.startswith('“') and len(nxt)<50 and nxt.endswith('말했다.')):para.keepWithNext=True
 flow.append(para)
def page(c,d):
 c.saveState();c.setFillColor(HexColor('#777777'));c.setFont('CustomerStory',8)
 if d.page>1:c.drawString(48,H-27,'고객 역할')
 c.drawCentredString(W/2,25,str(d.page));c.restoreState()
doc.build(flow,onFirstPage=page,onLaterPages=page);print(out)
