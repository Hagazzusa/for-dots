"""동일 좌표로 A4 3장의 실척 부품 시트를 만든다. 원본은 덮어쓰지 않도록 --out 사용 가능."""
from pathlib import Path
import argparse
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from build import SHAPES,shoe,ROOT
CUT=HexColor('#b04a44');FOLD=HexColor('#666666')
def path(c,pts,fill=None,stroke=None):
 p=c.beginPath();p.moveTo(*pts[0])
 for q in pts[1:]:p.lineTo(*q)
 p.close()
 if fill:c.setFillColor(HexColor(fill))
 if stroke:c.setStrokeColor(stroke)
 c.drawPath(p,fill=int(fill is not None),stroke=int(stroke is not None))
def footer(c,num):
 c.saveState();c.scale(mm,mm);c.setStrokeColor(CUT);c.setLineWidth(.2);c.line(20,15,70,15);c.line(20,13,20,17);c.line(70,13,70,17);c.setFillColor(HexColor('#333333'));c.setFont('Helvetica',3);c.drawString(20,19,'50 mm');c.drawString(80,14,'100%');c.drawRightString(190,14,str(num));c.restoreState()
def part(c,letter,layer,x,y):
 c.saveState();c.translate(x*mm,y*mm);c.scale(mm,mm)
 path(c,[(-62,-8),(62,-8),(62,0),(-62,0)],'#e6dbc4')
 for s in SHAPES:
  if (layer==0 and s['y']==0) or (layer!=0 and layer-1<s['y']<=layer):path(c,s['points'],s['color'])
 c.setLineWidth(.2)
 if letter in ['A','D']:outline=[(-62,-8),(62,-8),(62,0),(70,0),(70,110),(-70,110),(-70,0),(-62,0)]
 elif letter=='B':outline=[(-62,-8),(62,-8),(62,0),(70,0),(70,32)]+list(reversed(shoe))+[(-70,32),(-70,0),(-62,0)]
 else:outline=[(-62,-8),(62,-8),(62,0),(70,0),(70,25),(34,25),(34,100),(5,100),(5,25),(-70,25),(-70,0),(-62,0)]
 path(c,outline,stroke=CUT)
 if letter=='A':
  c.setStrokeColor(CUT)
  for xx in [-56,16]:c.rect(xx,32,40,56,fill=0,stroke=1)
 c.setDash(2,1);c.setStrokeColor(FOLD);c.line(-62,0,62,0);c.setDash()
 c.setFillColor(HexColor('#333333'));c.setFont('Helvetica',3);c.drawString(-60,-5,letter);c.restoreState()
def build(out):
 out.parent.mkdir(parents=True,exist_ok=True)
 c=Canvas(str(out),pagesize=(210*mm,297*mm),invariant=1,pageCompression=1)
 c.setTitle('The Other Shoe');c.setAuthor('dot');c.setSubject('140 x 80 x 110 mm paper theatre parts')
 part(c,'A',0,105,165);part(c,'D',80,105,30);footer(c,1);c.showPage()
 part(c,'B',28,105,220);part(c,'C',48,105,65);footer(c,2);c.showPage()
 c.saveState();c.scale(mm,mm);c.setLineWidth(.2)
 c.setFillColor(HexColor('#eee3cc'));c.setStrokeColor(CUT);c.rect(35,185,140,80,fill=1,stroke=1)
 c.setFont('Helvetica',3);c.setFillColor(HexColor('#555555'))
 for yy,name in [(0,'A'),(28,'B'),(48,'C'),(80,'D')]:
  c.setStrokeColor(FOLD);c.setDash(2,1);c.line(35,185+yy,175,185+yy);c.setDash();c.drawString(178,184+yy,name)
 c.setFont('Helvetica',4);c.drawString(35,175,'E')
 for x,name in [(20,'F'),(110,'G')]:
  c.setFillColor(HexColor('#eee3cc'));c.setStrokeColor(CUT);c.rect(x,32,80,118,fill=1,stroke=1)
  c.setDash(2,1);c.setStrokeColor(FOLD);c.line(x,40,x+80,40);c.setDash();c.setFillColor(HexColor('#333333'));c.drawString(x+2,35,name)
 c.restoreState();footer(c,3);c.save()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'output/The-Other-Shoe-Parts.pdf');a=p.parse_args();build(a.out);print(a.out)
