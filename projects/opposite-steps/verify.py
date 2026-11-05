#!/usr/bin/env python3
"""문제와 해설을 검사하고 모든 유효 상태의 이동을 별도 구현과 대조한다."""
from pathlib import Path
from itertools import permutations
import json
import solve
import independent_check as independent
P=Path(__file__).resolve().parent

def verify():
 data=json.loads((P/'puzzles.json').read_text());solutions=json.loads((P/'solutions.json').read_text())['solutions'];size=data['size'];checks=0;results=[]
 independent.rule_tests()
 for puzzle,saved in zip(data['puzzles'],solutions,strict=True):
  actual=solve.solve(puzzle,size)
  assert json.loads(json.dumps(actual))==saved
  assert saved['minimum']==[3,7,11][puzzle['id']-1] and saved['shortest_sequences']==1
  walls=set(puzzle['walls']);free=[i for i in range(size*size) if i not in walls]
  coord=lambda i:(i%size,i//size)
  wall_coords=set(map(coord,walls))
  for state in permutations(free,2):
   xy=tuple(map(coord,state))
   for command,name in enumerate(data['commands']):
    a=solve.move(state,command,walls,size)
    b,_=independent.move(xy,independent.DIRECTIONS[name],wall_coords,size)
    assert tuple(map(coord,a))==b
    checks+=1
  result=independent.solve(tuple(map(coord,puzzle['start'])),wall_coords,size)
  dist,count,_=result;goal=tuple(map(coord,puzzle['goal']))
  assert (dist[goal],count[goal],len(dist))==(saved['minimum'],1,saved['reachable_states'])
  assert saved['states'][0]==puzzle['start'] and saved['states'][-1]==puzzle['goal']
  assert all(list(solve.move(tuple(s),k,walls,size))==t for s,k,t in zip(saved['states'],saved['commands'],saved['states'][1:]))
  results.append({'문제':puzzle['id'],'최단 횟수':saved['minimum'],'최단 명령열 수':1,'도달 상태 수':len(dist)})
 return {'문제 검사':results,'독립 구현과 대조한 이동 수':checks,'기본 규칙 검사':5,'한계':'선정한 문제의 유한 상태 탐색 결과입니다. 실제 인쇄 및 사람 대상 플레이테스트는 하지 않았습니다.'}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
