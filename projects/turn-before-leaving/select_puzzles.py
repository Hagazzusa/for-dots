"""시드 41621의 후보 중 최단 4·8·12수인 첫 유일 해법 판을 고른다.

기본 실행은 JSON을 표준출력에만 쓴다. 기존 puzzles.json을 덮어쓰지 않는다.
"""
import random,json,sys
sys.dont_write_bytecode=True
from solve import solve

def select():
 r=random.Random(41621);found={}
 for _ in range(12000):
  p={'id':'','start':6,'goal':2,'arrows':[r.randrange(4) for _ in range(9)],'budget':5}
  s=solve(p)
  if not s or s['shortest_solutions']!=1:continue
  length=s['minimum_moves'];visited=[6]+[x['to'] for x in s['steps']]
  if length in (4,8,12) and length not in found and (length==4 or len(set(visited))<len(visited)):
   found[length]=p
  if len(found)==3:break
 assert len(found)==3
 out=[]
 for i,(_,p) in enumerate(sorted(found.items()),1):
  p['id']=str(i);p['name']=['돌려서 출발','돌아오면 다른 방향','바뀐 길 다시 쓰기'][i-1];out.append(p)
 return out
if __name__=='__main__':print(json.dumps(select(),ensure_ascii=False,indent=2))
