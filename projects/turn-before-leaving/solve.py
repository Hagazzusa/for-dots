"""한 칸을 떠나기 전의 두 선택을 너비 우선 탐색한다."""
from collections import deque
import json
from pathlib import Path
P=Path(__file__).resolve().parent
D=((0,-1),(1,0),(0,1),(-1,0))
def transitions(state, budget):
 pos, arrows, used=state
 for turn in (0,1):
  if used+turn>budget: continue
  a=(arrows[pos]+turn)%4
  x,y=pos%3,pos//3;dx,dy=D[a];xx,yy=x+dx,y+dy
  if not (0<=xx<3 and 0<=yy<3):continue
  b=list(arrows);b[pos]=a
  yield turn,(yy*3+xx,tuple(b),used+turn)
def solve(p):
 start=(p['start'],tuple(p['arrows']),0);goal=p['goal'];q=deque([start]);dist={start:0};ways={start:1};prev={};ends=[];best=None
 while q:
  s=q.popleft();depth=dist[s]
  if best is not None and depth>best:break
  if s[0]==goal:ends.append(s);best=depth;continue
  for turn,t in transitions(s,p['budget']):
   if t not in dist:
    dist[t]=depth+1;ways[t]=ways[s];prev[t]=(s,turn);q.append(t)
   elif dist[t]==depth+1:ways[t]+=ways[s]
 if not ends:return None
 e=ends[0];steps=[]
 while e!=start:
  s,turn=prev[e];steps.append({'from':s[0],'to':e[0],'turn':turn,'used':e[2]});e=s
 steps.reverse()
 return {'minimum_moves':best,'shortest_solutions':sum(ways[e] for e in ends),'steps':steps,'visited_states':len(dist)}
if __name__=='__main__':
 data=json.loads((P/'puzzles.json').read_text());out={p['id']:solve(p) for p in data}
 (P/'solutions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
