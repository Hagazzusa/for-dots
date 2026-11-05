from pathlib import Path
from fontTools.ttLib import TTFont as FTFont
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image

import argparse
parser = argparse.ArgumentParser(description='한국어 그림책 PDF 생성: 원본 PNG는 수정하지 않습니다.')
parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parent.parent)
parser.add_argument('--font', type=Path, required=True, help='설치된 NotoSerifCJK-Regular.ttc 파일')
parser.add_argument('--font-index', type=int, default=1, help='TTC의 한국어 글꼴 인덱스, 기본 1')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
BASE = args.output.resolve().parent
BASE.mkdir(parents=True, exist_ok=True)
REPO = args.repo.resolve()
# 저장소 루트 또는 독립 오프라인 사본의 형제 작품 폴더를 지원합니다.
if (REPO / 'projects').is_dir():
 REPO = REPO / 'projects'
scenes = [
 ('second-cup/renders/the_second_cup_final.png','두 잔의 자리','아직 따르지 않은 차', ['한 잔에 차를 따르고,','다른 잔은 그대로 두었다.','','돌아올 사람의 차가 식지 않도록,','따뜻함의 절반은 주전자에 남겨 두었다.']),
 ('a-place-for-rain/renders/a_place_for_rain_final.png','비를 내려놓을 자리','비는 여기까지',['문 앞에는 우산을 내려놓을 자리가 있다.','','비어 있는 문틈으로,','집 안의 빛이 먼저 마중 나왔다.']),
 ('morning-on-the-sill/renders/morning_on_the_sill_final.png','볕이 돌아온 창턱','아침은 조용히',['비가 지난 자리로 볕이 들었다.','','도자기 고양이 곁의 잎 두 장이,','말없이 밝아졌다.'])]
credits=['글·구성: dot · 그림: 직접 만든 정물의 실제 Blender Cycles 렌더', '게임의 결말이나 실제 개인사를 재현하지 않는 독립 이야기']
text='비가 지나가는 동안 세 장면으로 읽는 작은 그림책 123 / 끝.'+''.join(credits)+''.join(t+' '+h+' '.join(lines) for _,t,h,lines in scenes)
# A private subset is converted for ReportLab embedding; source font is unchanged.
f=FTFont(str(args.font), fontNumber=args.font_index)
sub=subset.Subsetter();sub.populate(text=text);sub.subset(f)
order=f.getGlyphOrder();glyphset=f.getGlyphSet();glyphs={}
for name in order:
 pen=TTGlyphPen(None); glyphset[name].draw(Cu2QuPen(pen,1.0,reverse_direction=True));glyphs[name]=pen.glyph()
fb=FontBuilder(f['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap());fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(dict(f['hmtx'].metrics));fb.setupHorizontalHeader(ascent=f['hhea'].ascent,descent=f['hhea'].descent)
fb.setupNameTable({'familyName':'QuietBook Embedded Subset','styleName':'Regular','uniqueFontIdentifier':'QuietBookSubset-Regular','fullName':'QuietBook Embedded Subset Regular','psName':'QuietBookSubset-Regular','copyright':'Noto Serif CJK, SIL Open Font License 1.1. Converted subset for document embedding.'})
fb.setupOS2(sTypoAscender=f['OS/2'].sTypoAscender,sTypoDescender=f['OS/2'].sTypoDescender,usWinAscent=f['OS/2'].usWinAscent,usWinDescent=f['OS/2'].usWinDescent);fb.setupPost();fb.setupMaxp()
font=BASE/'book-subset.ttf';fb.save(font);pdfmetrics.registerFont(TTFont('Book',str(font)))
out=args.output; w,h=510,680
c=canvas.Canvas(str(out),pagesize=(w,h),pageCompression=1,invariant=1)
c.setTitle('비가 지나가는 동안');c.setAuthor('dot');c.setSubject('세 정물과 여섯 문장으로 엮은 독립적인 작은 그림책')
def centered(text,y,size,color='#343d3a'):
 c.setFillColor(HexColor(color));c.setFont('Book',size);c.drawCentredString(w/2,y,text)
for i,(file,title,heading,lines) in enumerate(scenes):
 c.setFillColor(HexColor('#f4f0e8'));c.rect(0,0,w,h,fill=1,stroke=0)
 centered('비가 지나가는 동안',643,13);centered(f'{i+1} / 3',621,8,'#626962')
 image=Image.open(REPO/file);iw,ih=image.size;scale=min(422/iw,318/ih);dw,dh=iw*scale,ih*scale
 c.drawImage(ImageReader(image),(w-dw)/2,290+(318-dh)/2,width=dw,height=dh,mask='auto')
 centered(title,274,8,'#626962');centered(heading,233,20)
 y=194
 for line in lines:
  centered(line,y,12.5);y-=24 if line else 10
 if i==2:
  centered('끝.',65,10,'#626962')
  for j,line in enumerate(credits):centered(line,36-j*12,6.7,'#626962')
 else:centered('세 장면으로 읽는 작은 그림책',32,7,'#626962')
 c.showPage()
c.save();print(out)
