from pathlib import Path
from fontTools.ttLib import TTFont as FTFont
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape
P=Path(__file__).resolve().parent
source=(P/'play.txt').read_text();alltext=source+'확인 중0123456789\u2002'
def font(name,path):
 f=FTFont(path,fontNumber=1);ss=subset.Subsetter();ss.populate(text=alltext);ss.subset(f);order=f.getGlyphOrder();gs=f.getGlyphSet();glyphs={}
 for n in order:
  pen=TTGlyphPen(None);gs[n].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[n]=pen.glyph()
 fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
 fb.setupNameTable({'familyName':name,'styleName':'Regular','uniqueFontIdentifier':name,'fullName':name,'psName':name,'copyright':'Noto CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.'})
 fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
 dest=P/'tmp/pdfs'/f'{name}.ttf';fb.save(dest);pdfmetrics.registerFont(TTFont(name,str(dest)))
font('PlayText','/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc')
font('PlayName','/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
styles={
 'title':ParagraphStyle('Title',fontName='PlayText',fontSize=24,leading=32,spaceAfter=9,textColor=HexColor('#202724')),
 'subtitle':ParagraphStyle('Subtitle',fontName='PlayText',fontSize=10.5,leading=17,spaceAfter=20),
 'heading':ParagraphStyle('Heading',fontName='PlayName',fontSize=10,leading=17,spaceBefore=10,spaceAfter=5,keepWithNext=True),
 'intro':ParagraphStyle('Intro',fontName='PlayText',fontSize=10.5,leading=17,spaceAfter=6,wordWrap=None),
 'dialogue':ParagraphStyle('Dialogue',fontName='PlayText',fontSize=11.5,leading=18.5,leftIndent=35,firstLineIndent=-35,spaceAfter=4,wordWrap=None),
 'direction':ParagraphStyle('Direction',fontName='PlayText',fontSize=10.2,leading=17,leftIndent=35,rightIndent=6,spaceBefore=6,spaceAfter=8,textColor=HexColor('#4f5752'),wordWrap=None,keepWithNext=True),
}
W,H=480,680
out=P/'output/pdf/Under-Observation.pdf'
doc=SimpleDocTemplate(str(out),pagesize=(W,H),leftMargin=48,rightMargin=48,topMargin=45,bottomMargin=47,title='확인 중',author='닷돌이',subject='두 사람을 위한 독립적인 짧은 희곡',pageCompression=1)
flow=[];stage=False
for i,line in enumerate(source.splitlines()):
 if not line:continue
 if i==0:key='title'
 elif i==1:key='subtitle'
 elif line in ['등장인물','장소']:key='heading'
 elif line.startswith(('수진  ','경자  ')):
  key='dialogue';name,body=line.split('  ',1);line=f'<font name="PlayName">{name}</font>\u2002\u2002{escape(body)}'
  flow.append(KeepTogether([Paragraph(line,styles[key])]))
  stage=True;continue
 elif not stage:key='intro'
 else:key='direction'
 flow.append(Paragraph(escape(line),styles[key]))
def page(c,d):
 c.saveState();c.setFillColor(HexColor('#6d756f'));c.setFont('PlayText',8)
 if d.page>1:c.drawString(48,H-27,'확인 중')
 c.drawCentredString(W/2,25,str(d.page));c.restoreState()
doc.build(flow,onFirstPage=page,onLaterPages=page)
print(out)
