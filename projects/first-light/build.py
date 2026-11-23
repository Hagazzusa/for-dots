"""공동현관 우편함을 그린다. 외부 이미지나 서체를 읽지 않는다."""
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

W, H, S = 1050, 1400, 2
SIZE = (W*S, H*S)
rng = np.random.default_rng(4521)
picture = Image.new("RGB", SIZE, "#17232c")
d = ImageDraw.Draw(picture)


def position(x, y):
    return (round(S*x), round(S*(y-.092*(x-120))))


def polygon(points, color):
    d.polygon([position(x,y) for x,y in points], fill=color)


def rect(x,y,w,h,color):
    polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], color)


def line(points,color,width=1):
    d.line([position(x,y) for x,y in points], fill=color, width=round(S*width))


def disk(x,y,r,color):
    cx,cy=position(x,y)
    rr=round(r*S)
    d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=color)


# 왼쪽 문틀의 층과 벽 위에 덧댄 우편함 몸통.
rect(0,-100,128,H+200,"#383c41")
rect(0,-100,44,H+200,"#242930")
rect(44,-100,6,H+200,"#555452")
rect(67,-100,42,H+200,"#2b333a")
rect(103,-100,14,H+200,"#151e26")
rect(116,-70,880,1500,"#202b33")
rect(125,-20,865,1435,"#394a4c")
rect(126,-20,10,1435,"#566562")
rect(139,-20,4,1435,"#243339")
rect(970,-20,15,1435,"#24333b")
rect(987,-30,80,1470,"#343b40")
line([(1002,-50),(1002,1500)],"#555452",2)

# 도막은 칸마다 조금 다른 색으로 바랬다.
colors = [
    ["#425752","#415452","#3b5150"],
    ["#455b54","#42534d","#495850"],
    ["#40564e","#475850","#3d524f"],
    ["#43544e","#40534f","#405450"],
    ["#465854","#41534f","#3d4d4b"],
    ["#3c514d","#465552","#3d5250"],
]
width=257
for row, palette in enumerate(colors):
    y=14+row*238
    for col,color in enumerate(palette):
        x=152+col*274
        rect(x-3,y-3,width+7,229,"#222d34")
        rect(x,y,width,220,"#2c3d40")
        polygon([(x,y),(x+width,y),(x+width-7,y+6),(x+7,y+6),(x+7,y+211),(x,y+220)],"#5a6861")
        polygon([(x+width,y),(x+width,y+220),(x,y+220),(x+7,y+211),(x+width-7,y+211),(x+width-7,y+6)],"#33454a")
        rect(x+7,y+6,width-14,205,color)
        line([(x+10,y+209),(x+width-10,y+209)],"#58645a")
        # 사용한 손의 마찰과 도장에 남은 가는 균열.
        for _ in range(54):
            px=x+rng.uniform(11,width-16);py=y+rng.uniform(10,209)
            rgb=(int(rng.integers(65,87)),int(rng.integers(76,92)),int(rng.integers(70,83)))
            line([(px,py),(px+rng.uniform(.5,4),py+rng.uniform(-.7,.7))],rgb,.55)
        for _ in range(14):
            px=x+rng.uniform(45,210);py=y+rng.uniform(74,94)
            line([(px,py),(px+rng.uniform(1,6),py+rng.uniform(0,3))],"#566158",.6)
        if (row,col) in ((1,0),(2,1),(3,0),(4,2)):
            for _ in range(25):
                px=x+rng.normal(96,22);py=y+rng.normal(83,4)
                length=rng.uniform(.7,9)
                warm=(int(rng.integers(80,111)),int(rng.integers(84,103)),int(rng.integers(68,81)))
                line([(px,py),(px+length,py+length*.24)],warm,.48)
        sx=x+40
        rect(sx-2,y+47,185,32,"#303c3c")
        rect(sx,y+47,181,5,"#55665e")
        polygon([(sx,y+51),(sx+181,y+51),(sx+175,y+73),(sx+7,y+73)],"#17282b")
        rect(sx+8,y+55,165,14,"#152028")
        line([(sx+7,y+73),(sx+175,y+73)],"#6b7364",1.5)
        # 봉투 하나는 안으로 다 미끄러져 들어가지 않았다.
        if (row,col)==(1,2):
            polygon([(sx+23,y+58),(sx+151,y+57),(sx+147,y+65),(sx+34,y+67)],"#868274")
            line([(sx+39,y+62),(sx+142,y+60)],"#a09a7f",.8)
        # 이름표 자리. 한 칸에만 덮개가 떨어져 나갔다.
        bx,by=x+77,y+105
        if (row,col)==(2,1):
            rect(bx-2,by-1,104,36,"#6b7867")
            polygon([(bx,by),(bx+99,by),(bx+100,by+31),(bx+2,by+33)],"#29595b")
            line([(bx+2,by+32),(bx+97,by+31)],"#78a19a",1.15)
            # 판 모서리가 도막을 긁어 가져간 울퉁불퉁한 자국.
            polygon([(bx+8,by+31),(bx+14,by+31),(bx+17,by+29),(bx+22,by+31),
                     (bx+29,by+30),(bx+31,by+32),(bx+15,by+34)],"#858873")
            line([(bx+16,by+34),(bx+27,by+33)],"#98927b",.85)
            for dx in (5,94):
                disk(bx+dx,by+16,2.9,"#827c69")
                disk(bx+dx,by+15.5,1.65,"#223336")
            for px,py in [(bx+1,by+32),(bx+6,by+32),(bx+98,by+4),(bx+100,by+15)]:
                disk(px,py,1.1,"#b1a382")
        else:
            rect(bx+2,by+4,102,34,"#344442")
            rect(bx,by,102,34,"#75746a")
            rect(bx+5,by+4,92,24,"#a09984" if (row,col) in ((1,0),(3,2)) else "#827f70")
            line([(bx+4,by+4),(bx+98,by+4)],"#b0a68b",.8)
            line([(bx+7,by+28),(bx+97,by+28)],"#555950",1.1)
            if (row,col) in ((0,0),(1,0),(1,2),(3,0),(4,1),(5,2)):
                # 읽을 수 있는 주소 대신, 오래된 종이의 눌린 결만 그린다.
                for k in range(9):
                    lx=bx+22+k*4; ly=by+14+rng.normal(0,.3)
                    line([(lx,ly),(lx+rng.uniform(1,3),ly+rng.uniform(-.6,.6))],"#6f7268",1.25)

        disk(x+width-22,y+165,9,"#2b3938")
        disk(x+width-22,y+165,7,"#7a7a6a")
        line([(x+width-22,y+161),(x+width-22,y+168)],"#263335",1.7)
        line([(x+width-24,y+159),(x+width-20,y+159)],"#a0967e",.65)

# 입구 바깥에서 들어온 사다리꼴 빛. 칸과 틈에 따라 반사량이 다르다.
im = picture.resize((W,H),Image.Resampling.LANCZOS)
base = np.asarray(im).astype(np.float32)/255
yy,xx = np.mgrid[:H,:W]
penumbra = np.minimum((yy-(914-.70*xx))/2.2,((1144-.72*xx)-yy)/4.1)
light=np.clip(penumbra,0,1)*np.clip((xx-9)/90,0,1)
# 긴 빛 안쪽에 입구 문틀 그림자 하나를 남긴다.
shadow=np.clip(1-np.abs(xx-(883-.050*yy))/8.5,0,1)
light*=(1-.24*shadow)*(.66+.34*np.exp(-((xx-544)/355)**2))
sky=np.array([.87,.99,1.14],dtype=np.float32)
sun=np.array([1.56,1.39,1.07],dtype=np.float32)
wide = Image.fromarray(rng.integers(36,220, (170,132),dtype=np.uint8))
cloud = np.asarray(wide.resize((W,H),Image.Resampling.BICUBIC)).astype(np.float32)/255-.5
grain = rng.normal(0,.009,(H,W))+.023*cloud
ambient=np.clip(1.02-.22*((xx-430)/700)**2-.18*((yy-650)/1050)**2,.69,1.04)
shade=base*sky*ambient[:,:,None]
lit=base*sun + (base.mean(axis=2,keepdims=True)**1.4)*np.array([.30,.13,-.05])
result=shade+(lit-shade)*light[:,:,None]+grain[:,:,None]
result=np.clip(result*255+.5,0,255).astype(np.uint8)
target=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name("First-Light.jpg")
Image.fromarray(result).save(target,quality=92,optimize=True,subsampling=0)
