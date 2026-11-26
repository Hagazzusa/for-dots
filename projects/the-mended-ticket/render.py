"""Render a silent, fixed-camera vignette about a mended paper ticket."""
from pathlib import Path
import math
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, FPS, N = 864, 576, 24, 144
ROOT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def mix(a,b,t):
    return tuple(round(x+(y-x)*t) for x,y in zip(a,b))

def smooth(a,b,t):
    q = max(0,min(1,(t-a)/(b-a)))
    return q*q*(3-2*q)

bg = Image.new('RGB',(W,H),'#333333')
d = ImageDraw.Draw(bg)
rng = random.Random(76)
for y in range(H):
    for x in range(W):
        q = max(0,1-math.hypot((x-250)/720,(y-220)/620))
        v = rng.choice((-2,-1,0,0,0,1,2))
        bg.putpixel((x,y), tuple(c+v for c in mix((40,45,43),(66,70,58),q)))
# Window recess and soft sky; the rail goes in front of the background only.
d.polygon([(0,25),(435,47),(445,454),(0,486)],fill='#413e32')
d.polygon([(0,41),(414,61),(421,428),(0,449)],fill='#b5b6a1')
pane = Image.new('RGB',(425,392))
for y in range(pane.height):
    for x in range(pane.width):
        v=rng.choice((-1,0,0,0,1))
        q=min(1,y/370)
        c=mix((194,196,174),(218,205,158),q)
        pane.putpixel((x,y),tuple(a+v for a in c))
mask=Image.new('L',pane.size); ImageDraw.Draw(mask).polygon([(0,0),(414,20),(421,387),(0,391)],fill=255)
bg.paste(pane,(0,41),mask)
d.polygon([(0,406),(420,385),(421,428),(0,450)],fill='#d3c49c')
d.line([(195,50),(202,439)],fill='#777963',width=9)
d.line([(202,53),(209,438)],fill='#e6d9ae',width=3)
d.polygon([(0,450),(421,427),(445,443),(0,489)],fill='#8c7a5a')
d.line([(0,451),(421,427)],fill='#c5ad76',width=3)
d.line([(445,62),(456,438)],fill='#575849',width=2)
for i in range(32):
    x=rng.randrange(490,855);y=rng.randrange(18,562)
    d.line((x,y,x+1,y+rng.randrange(5,38)), fill=rng.choice(('#43463d','#494a3f','#48493e')))

rng = random.Random(12)
fibers = [(rng.randrange(12,400),rng.randrange(10,167),rng.randrange(1,7)) for _ in range(540)]
font_large = ImageFont.truetype(FONT,47)
font_small = ImageFont.truetype(FONT,16)
font_tiny = ImageFont.truetype(FONT,13)

def layer(light):
    im=Image.new('RGBA',(830,434))
    dd=ImageDraw.Draw(im)
    # An offset forefinger behind the stub; the thumb goes in front.
    dd.polygon([(384,97),(436,84),(485,98),(512,130),(828,286),(828,400),(449,191),(413,151)],fill='#926b53')
    dd.rounded_rectangle((375,81,472,130),radius=22,fill='#a77c60')
    dd.rounded_rectangle((5,7,417,171),radius=11,fill='#282e2870')
    paper=mix((159,147,110),(247,219,149),light)
    ink=mix((66,77,65),(107,96,65),light)
    dd.rounded_rectangle((4,4,412,167),radius=10,fill=paper)
    dd.rounded_rectangle((10,10,405,160),radius=7,outline=mix((124,116,90),(218,185,115),light))
    for x,y,z in fibers:
        dd.line((x,y,x+z,y-1), fill=mix(paper,(112,95,65),.12 if z%3 else .21))
    for y in range(16,155,8):
        dd.line((328,y,328,y+4),fill=mix(paper,ink,.56),width=1)
    dd.rectangle((21,28,307,33),fill=ink)
    dd.rectangle((21,129,307,131),fill=ink)
    dd.text((22,43),'RETURN',fill=ink,font=font_small)
    dd.text((18,63),'07:40',fill=ink,font=font_large)
    dd.text((145,139),'SERIES  X  /  061',fill=ink,font=font_tiny)
    # Translucent laid tissue: quiet in front light, denser in transmission.
    edge=[(226,5),(271,5),(269,10),(272,17),(269,30),(267,43),(269,55),
          (263,75),(241,83),(229,76),(226,59),(228,47),(224,34),(227,23)]
    resin=mix(paper,(190,142,87),.06+.47*light)
    # Preserve the ink below the tissue: tint each existing color toward the patch color.
    pm=Image.new('1',im.size)
    ImageDraw.Draw(pm).polygon(edge,fill=1)
    crop=(224,4,273,84)
    pm=pm.crop(crop)
    block=im.crop(crop)
    out=Image.blend(block, Image.new('RGBA',block.size,resin+(255,)),.16+.51*light)
    im.paste(out,crop,pm)
    dd.line([(249,5),(245,16),(252,25),(243,37),(246,45),(243,58),(235,68)],
            fill=mix(paper,(106,71,39),.14+.60*light),width=1+int(2*light))
    for i in range(9):
        x=229+((i*13)%38); y=12+((i*19)%52)
        if i != 5:
            dd.line((x,y,x+4,y-2),fill=mix(resin,paper,.21+.31*light))
    dd.ellipse((393,41,407,55),fill='#00000000')
    # Hand silhouette is deliberately cropped out of the picture on the right.
    dd.polygon([(382,111),(435,99),(475,110),(519,152),(828,283),(828,401),
                (522,289),(478,242),(454,192),(420,161),(381,152)],fill='#94664e')
    dd.rounded_rectangle((359,106,452,154),radius=23,fill='#b88969')
    dd.polygon([(422,108),(456,106),(475,118),(512,150),(518,180),(466,154),(424,147)],fill='#b88969')
    dd.arc((366,112,402,148),110,264,fill='#ce9f7d',width=2)
    dd.arc((431,122,461,152),260,349,fill='#996b50',width=2)
    return im

def frame(i):
    t = i / FPS
    progress=smooth(.55,3.35,t)-.043*smooth(3.28,3.87,t)
    light=smooth(.32,.90,progress)
    x,y=round(385-260*progress),round(326-157*progress)
    im=bg.copy()
    cur=Image.new("RGBA",(900,504))
    cur.alpha_composite(layer(light),(28,34))
    # Rotate a few degrees as the ticket is brought into alignment with the light.
    cur=cur.rotate(-7+10*progress,resample=Image.Resampling.BICUBIC, center=(405,169))
    im.paste(cur,(x-28,y-34),cur)
    return im

def main():
    comparison=Image.new('RGB',(W*2,H),'#222222')
    for n,i in enumerate((8,110)): comparison.paste(frame(i),(n*W,0))
    comparison.save(ROOT/'Before-and-Against-the-Light.jpg',quality=92,subsampling=0,optimize=True)
    if '--still' in sys.argv: return
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-threads','1',
         '-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'The-Mended-Ticket.mp4')]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as p:
        for i in range(N): p.stdin.write(frame(i).tobytes())
        p.stdin.close()
        if p.wait(): raise RuntimeError('FFmpeg encode failed')

if __name__=='__main__': main()
