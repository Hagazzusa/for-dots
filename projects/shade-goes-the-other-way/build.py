"""벤치 그림, 평행 격자, 서로 다른 재료의 A4 두 쪽을 한 좌표계로 그린다."""
import argparse
from pathlib import Path
from random import Random
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

PT = 72 / 25.4
W, H = 168, 78
X, Y, WW, WH = 20, 21, 126, 22
FX, FY, FW, FH = 4, 15, 160, 34
FONT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
SERIF = FONT.with_name('NotoSerifCJK-Regular.ttc')
INK = '#242e2c'
PAPER = '#eee7d6'
MARK = '#9a5742'
SHIFTS = (0, .5, 1)


class Drawing:
    def __init__(self, c, x, y):
        self.c, self.x, self.y = c, x, y

    def xy(self, x, y):
        return (self.x+x)*PT, (self.y-y)*PT

    def rect(self,x,y,w,h,fill=None,edge=None,sw=.2):
        c=self.c
        if fill: c.setFillColor(fill)
        if edge: c.setStrokeColor(edge); c.setLineWidth(sw*PT)
        u,v=self.xy(x,y+h)
        c.rect(u,v,w*PT,h*PT,stroke=bool(edge),fill=bool(fill))

    def poly(self, points, fill):
        c=self.c
        c.setFillColor(fill)
        p=c.beginPath()
        p.moveTo(*self.xy(*points[0]))
        for point in points[1:]: p.lineTo(*self.xy(*point))
        p.close()
        c.drawPath(p,stroke=0,fill=1)

    def line(self, points, color, sw=.2):
        c=self.c
        c.setStrokeColor(color); c.setLineWidth(sw*PT)
        p=c.beginPath(); p.moveTo(*self.xy(*points[0]))
        for point in points[1:]: p.lineTo(*self.xy(*point))
        c.drawPath(p,stroke=1,fill=0)

    def text(self, x,y,s,size=9,color=INK):
        self.c.setFillColor(color); self.c.setFont('Helvetica',size)
        self.c.drawString(*self.xy(x,y),s)

    def circle(self,x,y,r,fill):
        self.c.setFillColor(fill)
        self.c.circle(*self.xy(x,y),r*PT,stroke=0,fill=1)


def stripes(d, pitch, shift, lo, hi, color):
    for n in range(-5, 75):
        a=X+n*pitch+shift
        b=min(hi,a+pitch/2)
        a=max(lo,a)
        if b>a: d.rect(a,Y,b-a,WH,color)


def card(d, shift=None):
    r=Random(77)
    d.rect(0,0,W,H,'#2b3c38')
    d.rect(5,5,158,68,'#778781')
    d.rect(7,7,154,64,'#89928a')
    # 보이지 않는 마당 위 나무의 그림자. 줄무늬 바깥은 움직이지 않는다.
    for poly,col in [
       ([(7,7),(73,7),(65,11),(45,12),(33,16),(7,15)],'#657872'),
       ([(77,7),(99,7),(91,9),(76,11),(63,11)],'#70817a'),
       ([(7,13),(20,13),(30,16),(20,19),(7,22)],'#657c73'),
       ([(161,47),(149,49),(138,53),(126,54),(111,62),(161,63)],'#7b8478'),
    ]: d.poly(poly,col)
    d.rect(7,61.7,154,9.3,'#58685d')
    d.line([(7,62),(161,62)],'#a6a187',.4)
    d.line([(7,68),(161,68)],'#526257',.24)
    for i in range(220):
        x,y=r.uniform(7.4,160.4),r.uniform(7.4,70.6)
        d.line([(x,y),(min(x+r.uniform(.08,.64),160.8),y+r.uniform(-.13,.13))],
             r.choice(['#9a9f91','#7c8c81','#828a7e','#727e74']),r.uniform(.06,.13))
    # 벽에 나 있는 긴 틀과 그 안의 빛 우물.
    d.rect(16,19.4,136,25.4,INK)
    d.rect(X,Y,WW,WH,'#d2c6a4')
    stripes(d,2,0,X,X+WW,INK)
    if shift is not None: stripes(d,2.10,shift,X,X+WW,INK)
    d.line([(16,44.9),(152,44.9)],'#a4a08b',.24)
    # 빈 벤치의 발과 착석면. 나뭇결은 줄무늬와 따로 멈춰 있다.
    d.poly([(44,66),(121,66),(143,70),(52,70),(33,68)],'#495b53')
    for x in (52,110):
        d.poly([(x,48),(x+2.2,48),(x+4.8,68),(x+2.2,68)],'#303a36')
        d.poly([(x+8,60),(x+10.3,60),(x+7.6,68.4),(x+5.3,68.4)],'#242f2b')
    d.poly([(45,48),(120,48),(125,53),(48,53)],'#4e493c')
    d.poly([(45,47.3),(119.5,47.3),(123,50.9),(47.2,50.9)],'#bb976a')
    d.poly([(48.2,52.1),(123.4,52.1),(126,55.1),(50.7,55.1)],'#a57c55')
    d.line([(49,48),(118,48)],'#d5b58c',.23)
    d.line([(52,52.7),(121,52.7)],'#c7a57a',.2)
    d.poly([(48,56.6),(125.2,56.6),(131.4,60),(48.8,60)],'#c9a77b')
    d.poly([(48.8,60),(131.4,60),(131.4,61.05),(48.8,61.05)],'#806348')
    for x in (56,113):
        for y in (49.2,53.2): d.circle(x,y,.29,'#554b3c')
    for i in range(38):
        x,y=r.uniform(58,108),r.choice([48.6,49.9,53.4,54.3,58,59.2])
        d.line([(x,y),(x+r.uniform(.2,4.8),y+r.uniform(-.09,.09))],
               r.choice(['#ae865f','#d1ad81','#a78260']),.09)
    for x,y in [(73,58.1),(76,58.5),(36,65.3),(29,68.2),(142,66.1)]:
        d.poly([(x-1.2,y+.2),(x,y-.7),(x+1.55,y-.1),(x+.45,y+.55)],'#d2ae70')
        d.line([(x-.5,y+.25),(x+.8,y-.1)],'#8c6c4d',.12)
    d.line([(6.95,7),(6.95,71),(161,71)],'#a6a393',.22)


def make_template(path):
    c=canvas.Canvas(str(path),pagesize=(210*PT,297*PT),invariant=1,pageCompression=1)
    c.setTitle('Shade Goes the Other Way')
    for i in (1,2):
        d=Drawing(c,0,297)
        d.text(21,28,'SHADE GOES THE OTHER WAY',16)
        if i==1:
            d.text(21,39,'01  /  A4   PAPER',10)
            card(Drawing(c,21,297-57))
            d.rect(21,57,W,H,edge=MARK,sw=.18)
            # 필름 왼쪽 테두리를 맞출 작은 눈금: 시작과 끝.
            for nx in (21+FX,21+FX+2.10):
                d.line([(nx,68.8),(nx,71.1)],'#ded1af',.25)
            d.line([(21+.9,57+FY),(21+3.4,57+FY)],'#ded1af',.25)
            d.line([(21+166.6,57+FY),(21+167.8,57+FY)],'#ded1af',.25)
            d.text(21,151,'A   /   168 x 78 mm',10)
            d.text(21,159,'FIXED      2.00 mm',9)
        else:
            d.text(21,39,'02  /  A4   CLEAR FILM',10)
            # 완성 겹침 좌표를 유지하되 필름 왼쪽 테두리를 종이 x=21에 둔다.
            f=Drawing(c,21-FX,297-57+FY)
            f.rect(FX,FY,FW,FH,edge=MARK,sw=.18)
            stripes(f,2.10,0,17.5,149,'#000000')
            f.line([(FX,FY+1),(FX,FY+3)],'#5e5747',.2)
            d.text(21,111,'B   /   160 x 34 mm',10)
            d.text(21,119,'SLIDER     2.10 mm',9)
        d.line([(21,258),(71,258)],INK,.20)
        for x in (21,71): d.line([(x,256.4),(x,259.6)],INK,.20)
        d.text(21,253,'50 mm',9)
        d.text(101,258,'PRINT   100%   /   NO FIT TO PAGE',9)
        c.showPage()
    c.save()


def render_card(shift):
    with TemporaryDirectory() as temp:
        pdf=Path(temp)/'card.pdf'
        c=canvas.Canvas(str(pdf),pagesize=(W*PT,H*PT),invariant=1)
        card(Drawing(c,0,H),shift); c.showPage(); c.save()
        subprocess.run(['pdftoppm','-q','-singlefile','-png','-r','420',str(pdf),str(Path(temp)/'card')],check=True)
        with Image.open(Path(temp)/'card.png') as im:
            im.load()
            return im.convert('RGB').resize((900,418),Image.Resampling.LANCZOS)


def make_preview(path):
    im=Image.new('RGB',(980,1648),PAPER)
    d=ImageDraw.Draw(im)
    def text(x,y,t,size,font=FONT):
        d.text((x,y),t,font=ImageFont.truetype(str(font),size,index=1),fill=INK,anchor='lt')
    text(40,43,'그늘은 반대로',59,SERIF)
    text(43,132,'필름을 오른쪽으로  ·  그늘은 왼쪽으로',29)
    for i,shift in enumerate(SHIFTS):
        top=204+474*i
        text(40,top,f'0{i+1}   /   오른쪽  +{shift:.2f} mm',27)
        im.paste(render_card(shift),(40,top+40))
    im.save(path,quality=93,subsampling=0,optimize=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('folder',nargs='?',type=Path,default=Path(__file__).resolve().parent)
    a=p.parse_args()
    a.folder.mkdir(exist_ok=True)
    make_template(a.folder/'Shade-Goes-the-Other-Way-Print.pdf')
    make_preview(a.folder/'Shade-Goes-the-Other-Way.jpg')
