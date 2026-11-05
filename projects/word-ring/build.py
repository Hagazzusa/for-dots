from pathlib import Path
from fontTools.ttLib import TTFont as FTFont
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape
P=Path(__file__).resolve().parent
import json,math
D=json.loads((P/'words.json').read_text());words=D['words'];title=D['title'];caption='이웃한 낱말 사이에서 한 글자씩 바뀝니다.'
alltext=''.join(words)+title+caption
f=FTFont('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',fontNumber=1);ss=subset.Subsetter();ss.populate(text=alltext);ss.subset(f);order=f.getGlyphOrder();gs=f.getGlyphSet();glyphs={}
for n in order:
 pen=TTGlyphPen(None);gs[n].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[n]=pen.glyph()
fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
fb.setupNameTable({'familyName':'WordRing','styleName':'Regular','uniqueFontIdentifier':'WordRing','fullName':'WordRing','psName':'WordRing','copyright':'Noto CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.'})
fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
dest=P/'tmp/pdfs/WordRing.ttf';dest.parent.mkdir(parents=True,exist_ok=True);fb.save(dest);pdfmetrics.registerFont(TTFont('WordRing',str(dest)))

# 낱말은 돌리지 않고 원 위에 놓는다. 새 글자만 검게 인쇄한다.
from reportlab.pdfgen.canvas import Canvas
from fontTools.pens.svgPathPen import SVGPathPen
W,H=600,650;CX,CY,R=300,340,218;FS=18
out=P/'Word-Ring.pdf';c=Canvas(str(out),pagesize=(W,H),pageCompression=1)
c.setTitle(title);c.setAuthor('닷돌이');c.setSubject('스물여섯 낱말을 잇는 원형 글자 그림')
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',f'<title id="title">{title}</title>', '<desc id="desc">스물여섯 낱말이 원을 이룹니다. 시계방향으로 이웃한 낱말의 한 글자만 바뀌며, 바뀐 글자는 검정, 남은 글자는 회색입니다.</desc>','<rect width="100%" height="100%" fill="white"/>']
font=FTFont(dest);glyphset=font.getGlyphSet();cmap=font.getBestCmap();units=font['head'].unitsPerEm
def glyph(ch,x,y,size,color):
 c.setFillColor(HexColor(color));c.setFont('WordRing',size);c.drawString(x,y,ch)
 pen=SVGPathPen(glyphset);glyphset[cmap[ord(ch)]].draw(pen);path=pen.getCommands()
 svg.append(f'<path fill="{color}" transform="translate({x:.6f},{H-y:.6f}) scale({size/units:.9f},{-size/units:.9f})" d="{path}"/>')
def line(text,x,y,size,color):
 for ch in text:
  glyph(ch,x,y,size,color);x+=pdfmetrics.stringWidth(ch,'WordRing',size)
records=[]
for i,word in enumerate(words):
 prev=words[(i-1)%len(words)];changed=[j for j in range(2) if word[j]!=prev[j]];assert len(changed)==1
 angle=math.pi/2-2*math.pi*i/len(words);x=CX+R*math.cos(angle);y=CY+R*math.sin(angle)-FS*.36
 svg.append(f'<g aria-label="{word}">')
 for j,ch in enumerate(word):glyph(ch,x-FS+j*FS,y,FS,'#202020' if j==changed[0] else '#858585')
 svg.append('</g>');records.append({'word':word,'changed_position':changed[0],'center':[x,y+FS*.36],'baseline':y,'box':[x-FS,y-FS*.16,x+FS,y+FS*.9]})
for text,y,size in [(title,64,16),(caption,42,9)]:line(text,(W-pdfmetrics.stringWidth(text,'WordRing',size))/2,y,size,'#202020')
svg.append('</svg>');(P/'Word-Ring.svg').write_text('\n'.join(svg)+'\n')
c.showPage();c.save();(P/'layout.json').write_text(json.dumps({'page':[W,H],'radius':R,'word_font_size':FS,'words':records},ensure_ascii=False,indent=2)+'\n');print(out)
