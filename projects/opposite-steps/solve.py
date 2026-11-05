#!/usr/bin/env python3
"""4×4 반대 방향 이동 퍼즐의 도달 상태와 최단 명령열을 탐색한다."""
from pathlib import Path
from collections import deque
import json
ROOT=Path(__file__).resolve().parent
DIRECTIONS=((-1,0),(0,1),(1,0),(0,-1))

def move(state,command,walls,size=4):
 def proposal(pos,dr,dc):
  row,col=divmod(pos,size);row+=dr;col+=dc
  if not (0<=row<size and 0<=col<size) or row*size+col in walls:return pos
  return row*size+col
 a,b=state;dr,dc=DIRECTIONS[command]
 aa=proposal(a,dr,dc);bb=proposal(b,-dr,-dc)
 if aa==bb or (aa==b and bb==a):return state
 return aa,bb

def solve(puzzle,size=4):
 walls=set(puzzle['walls']);start=tuple(puzzle['start']);goal=tuple(puzzle['goal'])
 assert len(set(start+goal))==4 and all(0<=p<size*size and p not in walls for p in start+goal)
 distance={start:0};count={start:1};parent={start:None};queue=deque([start])
 while queue:
  state=queue.popleft()
  for command in range(4):
   new=move(state,command,walls,size)
   if new not in distance:
    distance[new]=distance[state]+1;count[new]=count[state];parent[new]=(state,command);queue.append(new)
   elif distance[new]==distance[state]+1:count[new]+=count[state]
 assert goal in distance
 commands=[];states=[goal];state=goal
 while parent[state] is not None:
  previous,command=parent[state];commands.append(command);states.append(previous);state=previous
 commands.reverse();states.reverse()
 return {'id':puzzle['id'],'minimum':distance[goal],'shortest_sequences':count[goal],'reachable_states':len(distance),'commands':commands,'states':states}

def main():
 data=json.loads((ROOT/'puzzles.json').read_text());results=[solve(p,data['size']) for p in data['puzzles']]
 (ROOT/'solutions.json').write_text(json.dumps({'commands':data['commands'],'solutions':results},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
