from pathlib import Path
import math,json,sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
P=Path(__file__).resolve().parent
layout=sys.argv[1] if len(sys.argv)>1 else 'final'
assert layout in ('final','four','six')
ids=[0,3,4,5] if layout in ('four','final') else list(range(6));rows=len(ids)//2
W,H=760,(540 if layout in ('four','final') else 800);M=22;G=16;PW=(W-2*M-G)/2;PH=(H-2*M-(rows-1)*G)/rows
INK='#293a3d';PAPER='#f5efe4';FRAME='#d9cfc0';GROUND='#c7bcac';SKIN='#d5b69c';BLUE='#4d7180';RUST='#b3664e';PANTS='#38464a';WOOD='#a47e51';WOOD_DARK='#80613f';WOOD_LIGHT='#bd9c70'
out=P/'output/pdf/While-Carrying.pdf' if layout=='final' else P/f'studies/While-Carrying-{layout}.pdf'
c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1);c.setTitle('옮기는 동안');c.setAuthor('닷돌이');c.setSubject('말 없는 네 칸 만화' if len(ids)==4 else '말 없는 여섯 칸 비교본')
c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
def line(points,color,width):
 c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setLineCap(1);c.setLineJoin(1);p=c.beginPath();p.moveTo(*points[0])
 for v in points[1:]:p.lineTo(*v)
 c.drawPath(p,stroke=1,fill=0)
def poly(points,color,outline=None,w=.8):
 p=c.beginPath();p.moveTo(*points[0])
 for v in points[1:]:p.lineTo(*v)
 p.close();c.setFillColor(HexColor(color));c.setStrokeColor(HexColor(outline or color));c.setLineWidth(w);c.drawPath(p,fill=1,stroke=bool(outline))
def ellipse(x,y,rx,ry,color):
 c.setFillColor(HexColor(color));c.ellipse(x-rx,y-ry,x+rx,y+ry,fill=1,stroke=0)
def bench(x,y,L=130):
 # Rear legs and narrow lower stretchers first, then front legs and seat.
 for xx in [x+21,x+L-5]:poly([(xx-3,y+6),(xx+3,y+6),(xx+5,y-31),(xx-1,y-31)],WOOD_DARK)
 line([(x+22,y-22),(x+L-4,y-22)],WOOD_DARK,3)
 for xx in [x+12,x+L-12]:poly([(xx-3,y),(xx+3,y),(xx+4,y-37),(xx-2,y-37)],WOOD_DARK)
 line([(x+12,y-27),(x+L-12,y-27)],WOOD_DARK,3)
 poly([(x,y),(x+L,y),(x+L,y+5),(x,y+5)],WOOD_DARK)
 poly([(x,y+5),(x+L,y+5),(x+L+7,y+11),(x+7,y+11)],WOOD_LIGHT)
 line([(x+8,y+8),(x+L-1,y+8)],WOOD,0.65)
def person(x,hip,base,coat,mode='stand',reach=None,side=1,gaze=0,stride=0,gesture=None):
 # Legs: a wider squat and clearly bent seated knees distinguish the pauses.
 if mode=='sit':
  knees=[(x-15,base+39),(x+15,base+39)];feet=[(x-17,base+3),(x+18,base+3)]
 elif mode=='squat':
  knees=[(x-22,base+29),(x+22,base+29)];feet=[(x-18,base+3),(x+20,base+3)]
 else:
  knees=[(x-7+stride*.35,base+31),(x+7-stride*.35,base+32)];feet=[(x-8+stride,base+3),(x+9-stride,base+3+(5 if stride else 0))]
 for i in range(2):
  line([(x+(-6 if i==0 else 6),hip),knees[i],feet[i]],PANTS,8)
  ellipse(feet[i][0]+2,feet[i][1],7,3,INK)
 # Back/outer arm.
 if mode=='sit' and gesture=='relax':
  line([(x-side*10,hip+35),(x-side*20,hip+16),(x-side*22,hip-3)],coat,7);ellipse(x-side*22,hip-3,4,2.3,SKIN)
 elif mode=='sit':
  line([(x-side*10,hip+35),(x-side*17,hip+16),(x-side*13,base+43)],coat,7);ellipse(x-side*13,base+43,3,3,SKIN)
 else:
  line([(x-side*10,hip+35),(x-side*14,hip+17),(x-side*10,hip+2)],coat,7);ellipse(x-side*10,hip+2,3,3,SKIN)
 # Rounded coat silhouette.
 p=c.beginPath();p.moveTo(x-6,hip+43);p.curveTo(x-14,hip+42,x-16,hip+31,x-13,hip+20);p.lineTo(x-11,hip-1);p.curveTo(x-3,hip-4,x+6,hip-4,x+13,hip);p.lineTo(x+12,hip+29);p.curveTo(x+14,hip+39,x+7,hip+43,x+4,hip+43);p.close();c.setFillColor(HexColor(coat));c.drawPath(p,fill=1,stroke=0)
 # Neck and a deliberately spare face.
 poly([(x-3,hip+40),(x+4,hip+40),(x+4,hip+49),(x-3,hip+49)],SKIN)
 hx=x+gaze*.6;hy=hip+57
 ellipse(hx,hy,10,12,SKIN)
 p=c.beginPath();p.moveTo(hx-10,hy+1);p.curveTo(hx-13,hy+16,hx+5,hy+17,hx+10,hy+5);p.curveTo(hx+3,hy+9,hx-4,hy+8,hx-10,hy+1);p.close();c.setFillColor(HexColor(INK));c.drawPath(p,fill=1,stroke=0)
 if abs(gaze)>=2:
  direction=1 if gaze>0 else -1
  poly([(hx+direction*8,hy+3),(hx+direction*13,hy-1),(hx+direction*8,hy-3)],SKIN)
  ellipse(hx+direction*5,hy+2,.7,.8,INK)
  line([(hx+direction*6,hy-5),(hx+direction*9,hy-5)],INK,.6)
 else:
  for ex in [-3,3]:ellipse(hx+ex+gaze*.8,hy+1,.65,.75,INK)
  line([(hx+gaze*.5-1.3,hy-5),(hx+gaze*.5+1.4,hy-5.2)],INK,.6)
 # Inner hand is at the actual bench corner while carrying/lowering.
 if reach is not None:
  line([(x+side*10,hip+35),(x+side*21,reach[1]+10),reach],coat,7);ellipse(*reach,3,3,SKIN)
 elif gesture=='invite':
  line([(x+side*10,hip+35),(x+side*23,hip+13),(x+side*34,hip-3)],coat,7);ellipse(x+side*34,hip-3,5,2.3,SKIN)
 elif mode=='sit' and gesture=='relax':
  line([(x+side*10,hip+35),(x+side*20,hip+16),(x+side*22,hip-3)],coat,7);ellipse(x+side*22,hip-3,4,2.3,SKIN)
 elif mode=='sit':
  line([(x+side*10,hip+35),(x+side*17,hip+16),(x+side*13,base+43)],coat,7);ellipse(x+side*13,base+43,3,3,SKIN)
 else:
  line([(x+side*10,hip+35),(x+side*14,hip+16),(x+side*9,hip+1)],coat,7);ellipse(x+side*9,hip+1,3,3,SKIN)

records=[]
for index,i in enumerate(ids):
 row=index//2;col=index%2;ox=M+col*(PW+G);oy=H-M-(row+1)*PH-row*G;c.saveState();c.translate(ox,oy)
 c.setStrokeColor(HexColor(FRAME));c.setLineWidth(.7);c.rect(0,0,PW,PH,fill=0,stroke=1)
 ground=48
 line([(16,ground),(PW-16,ground)],GROUND,.65)
 # A fixed small crack is a location cue rather than a motion arrow.
 line([(49,ground),(53,ground-3),(57,ground),(63,ground-2)],GROUND,.7)
 bx=[74,94,108,108,108,108][i];by=ground+([70,50,37,37,37,37][i]);L=130
 ellipse(bx+L/2+3,ground+2,L/2+8,4,'#e5daca')
 bench(bx,by,L)
 if i==0:
  person(bx-21,ground+66,ground,BLUE,reach=(bx+1,by+4),side=1,gaze=2,stride=-4)
  person(bx+L+21,ground+66,ground,RUST,reach=(bx+L,by+4),side=-1,gaze=-2,stride=-8)
 elif i==1:
  person(bx-21,ground+47,ground,BLUE,mode='squat',reach=(bx+1,by+4),side=1,gaze=1)
  person(bx+L+21,ground+47,ground,RUST,mode='squat',reach=(bx+L,by+4),side=-1,gaze=-1)
 elif i==2:
  person(bx-21,ground+66,ground,BLUE,side=1,gaze=1)
  person(bx+L+21,ground+66,ground,RUST,side=-1,gaze=-1)
 elif i==3:
  person(bx+31,ground+46,ground,BLUE,mode='sit',side=1,gaze=0)
  person(bx+L+21,ground+66,ground,RUST,side=-1,gaze=-2)
 elif i==4:
  person(bx+31,ground+46,ground,BLUE,mode='sit',side=1,gaze=2,gesture='invite')
  person(bx+L-24,ground+66,ground,RUST,side=-1,gaze=-2)
 else:
  person(bx+31,ground+46,ground,BLUE,mode='sit',side=1,gaze=0,gesture='relax')
  person(bx+L-24,ground+46,ground,RUST,mode='sit',side=-1,gaze=0)
 records.append({'panel':index+1,'source_scene':i+1,'origin':[ox,oy],'panel_size':[PW,PH],'bench_length':L,'bench_left':bx,'seat_base_y':by,'bench_front_feet_y':by-37,'ground_y':ground})
 c.restoreState()
c.showPage();c.save();(P/('geometry.json' if layout=='final' else f'studies/{layout}-geometry.json')).write_text(json.dumps(records,indent=2)+'\n')
