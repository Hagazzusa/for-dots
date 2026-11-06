"""회전 화살표 퍼즐의 문제지와 해설을 만든다. --output-root로 별도 재생성이 가능하다."""
from pathlib import Path
import argparse,json,math,tempfile
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor,black,white
from font_support import register_reading_font,FONT_NAME
P=Path(__file__).resolve().parent
W,H=595.28,841.89
INK='#183e41';ORANGE='#b54a2b'
def label(i):return 'ABC'[i%3]+str(i//3+1)
def text(c,x,y,s,size=11,color=INK):
 c.setFillColor(HexColor(color));c.setFont(FONT_NAME,size);c.drawString(x,y,s)
def line(c,x,y,s,size=11):text(c,x,y,s,size)
def arrow(c,x,y,d,size=18,color=INK):
 dx,dy=((0,1),(1,0),(0,-1),(-1,0))[d];px,py=-dy,dx
 c.setStrokeColor(HexColor(color));c.setLineWidth(2.2)
 a=(x-dx*size*.6,y-dy*size*.6);b=(x+dx*size*.6,y+dy*size*.6)
 c.line(*a,*b)
 c.line(*b,b[0]-dx*size*.43+px*size*.32,b[1]-dy*size*.43+py*size*.32)
 c.line(*b,b[0]-dx*size*.43-px*size*.32,b[1]-dy*size*.43-py*size*.32)
def grid(c,p,x,y,cell=90,blank=False):
 # y는 판의 아랫변이다.
 for i in range(9):
  xx=x+(i%3)*cell;yy=y+(2-i//3)*cell
  c.setFillColor(HexColor('#e9f1ef' if i==p['goal'] else '#ffffff'))
  c.setStrokeColor(HexColor('#72918d'));c.setLineWidth(.7);c.rect(xx,yy,cell,cell,fill=1)
  text(c,xx+6,yy+cell-15,label(i),9)
  if i==p['goal']:text(c,xx+cell*.27,yy+cell*.43,'도착',13)
  elif not blank:arrow(c,xx+cell/2,yy+cell/2,p['arrows'][i],cell*.25)
  if i==p['start']:text(c,xx+6,yy+8,'출발',9,ORANGE)
def footer(c,n):text(c,48,26,'떠나기 전에 한 번',8);text(c,W-58,26,str(n),8)
def circles(c,x,y):
 for k in range(5):c.setStrokeColor(HexColor(INK));c.setLineWidth(.9);c.circle(x+28*k,y,7,fill=0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-root',type=Path,default=P/'output');args=ap.parse_args();out=args.output_root/'pdf';out.mkdir(parents=True,exist_ok=True)
 ps=json.loads((P/'puzzles.json').read_text());ss=json.loads((P/'solutions.json').read_text())
 # 동적으로 쓰는 칸 이름과 수를 더한다. 본문은 이 파일 안에 보존한다.
 chars=Path(__file__).read_text()+json.dumps(ps,ensure_ascii=False)+'ABC0123456789→'
 with tempfile.TemporaryDirectory() as td:
  register_reading_font(Path('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'),chars,Path(td))
  c=Canvas(str(out/'Before-You-Leave.pdf'),pagesize=(W,H),invariant=1);c.setTitle('떠나기 전에 한 번');c.setAuthor('닷돌이')
  for n,p in enumerate(ps,1):
   text(c,48,H-66,'떠나기 전에 한 번',24);text(c,48,H-95,f"문제 {n} · {p['name']}",13)
   rules=['말 한 개를 A3에 놓고 C1까지 옮기세요.', '한 번 움직일 때, 현재 칸 화살표를 그대로 두거나', '시계방향으로 90도 한 번 돌린 뒤 그 방향으로 한 칸 갑니다.', '돌린 화살표는 그대로 남습니다. 회전은 총 다섯 번까지입니다.', '판 밖으로 가는 선택과 제자리 회전은 할 수 없습니다.', '도착 칸에 들어가면 끝입니다. 더 적게 움직이는 길도 찾아보세요.']
   for k,s in enumerate(rules):text(c,48,H-137-k*19,s,11)
   grid(c,p,162,245)
   text(c,162,218,'쓴 회전 횟수',10);circles(c,270,222)
   text(c,48,146,'종이에 판을 연필로 옮겨 그리면 방향을 지우고 고칠 수 있습니다.',10)
   text(c,48,125,'또는 4쪽의 판과 화살표 조각을 사용하세요. 막히면 처음부터 다시 시작합니다.',9.5)
   text(c,48,96,'시계방향 순서',10)
   for k in range(4):arrow(c,166+48*k,99,k,14)
   text(c,365,95,'다시 위 방향',9)
   footer(c,n);c.showPage()
  text(c,48,H-66,'옮겨 놓는 판과 화살표',23)
  text(c,48,H-99,'아래 조각을 잘라 문제의 시작 방향대로 올려놓으세요.',11)
  text(c,48,H-120,'회전할 때 조각을 돌립니다. 목표 칸에는 놓지 않고, 한 조각은 여분입니다.',10)
  grid(c,ps[0],162,390,blank=True)
  text(c,48,340,'화살표 조각 · 각 25mm 안팎 · 가위 사용 시 주의하세요',11)
  for i in range(9):
   x=60+(i%5)*96;y=224-(i//5)*96
   c.setDash(3,3);c.setStrokeColor(HexColor('#72918d'));c.setLineWidth(.6);c.rect(x,y,70,70);c.setDash()
   arrow(c,x+35,y+35,0,23)
  footer(c,4);c.showPage();c.save()
  c=Canvas(str(out/'Before-You-Leave-Solutions.pdf'),pagesize=(W,H),invariant=1);c.setTitle('떠나기 전에 한 번 해설');c.setAuthor('닷돌이')
  for n,p in enumerate(ps,1):
   s=ss[p['id']];text(c,48,H-64,f"문제 {n} · {p['name']}",22)
   text(c,48,H-94,f"최단 {s['minimum_moves']}번 이동 · 회전 {s['steps'][-1]['used']}번",13)
   text(c,48,H-119,'각 문제의 최단 선택열은 하나입니다. 더 긴 해법도 규칙에 맞으면 정답입니다.',9.5)
   grid(c,p,353,540,cell=60)
   text(c,48,679,'순서',10);text(c,97,679,'출발 → 다음 칸',10);text(c,220,679,'현재 칸에서',10)
   for k,step in enumerate(s['steps'],1):
    y=651-(k-1)*26;text(c,48,y,str(k));text(c,97,y,label(step['from'])+' → '+label(step['to']))
    text(c,220,y,'90도 돌림' if step['turn'] else '그대로',11,ORANGE if step['turn'] else INK)
   commentary=[['A3의 왼쪽 화살표를 위로 돌려 출발합니다.','C2에서는 왼쪽을 위로 돌려 도착합니다.'],['B3로 돌아올 때마다 처음 방향이라고 생각하면 막힙니다.','한 번 돌린 B3는 위, 두 번 돌린 뒤에는 오른쪽을 가리킵니다.'],['C3은 두 번, C2는 세 번 돌려 길을 만듭니다.','뒤쪽의 긴 우회에서는 이미 바꿔 둔 화살표를 그대로 씁니다.']][n-1]
   yy=266
   for t in commentary:text(c,48,yy,t,11);yy-=23
   text(c,48,174,'좌표는 왼쪽부터 A·B·C, 위에서부터 1·2·3입니다.',10)
   text(c,48,152,'최단 이동수는 너비 우선 탐색과 별도 구현으로 확인했습니다.',10)
   text(c,48,130,'실물 플레이테스트는 하지 않았으며 이 수치가 체감 난이도를 뜻하지는 않습니다.',9.5)
   footer(c,n);c.showPage()
  c.save()
if __name__=='__main__':main()
