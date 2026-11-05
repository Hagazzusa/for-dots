from pathlib import Path
from itertools import combinations
import json
P=Path(__file__).resolve().parent
N=5;FULL=(1<<25)-1
SHAPES={'A':[(0,0),(1,0),(2,0)],'B':[(0,0),(0,1),(1,1)],'C':[(0,0),(1,0),(0,1),(1,1),(0,2)],'D':[(0,0),(2,0),(0,1),(1,1),(2,1)]}
def orientations(cells):
 out=set()
 for flip in [False,True]:
  pts=[(-x if flip else x,y) for x,y in cells]
  for k in range(4):
   xmin=min(x for x,y in pts);ymin=min(y for x,y in pts)
   out.add(tuple(sorted((x-xmin,y-ymin) for x,y in pts)))
   pts=[(-y,x) for x,y in pts]
 return sorted(out)
places={}
for name,cells in SHAPES.items():
 places[name]=[]
 for shape in orientations(cells):
  w=max(x for x,y in shape)+1;h=max(y for x,y in shape)+1
  for oy in range(N-h+1):
   for ox in range(N-w+1):
    cells=tuple((x+ox,y+oy) for x,y in shape);mask=sum(1<<(y*N+x) for x,y in cells)
    places[name].append((mask,cells))
paths=[]
for right_steps in combinations(range(8),4):
 x=y=0;cells=[(x,y)]
 for step in range(8):
  if step in right_steps:x+=1
  else:y+=1
  cells.append((x,y))
 paths.append(cells)
solutions=[]
for path in paths:
 pathmask=sum(1<<(y*N+x) for x,y in path)
 available={name:[v for v in vals if not v[0]&pathmask] for name,vals in places.items()}
 def fill(occupied,remaining,chosen):
  if not remaining:
   assert occupied|pathmask==FULL
   solutions.append({'path':path,'pieces':dict(chosen)});return
  target=next(i for i in range(25) if not ((occupied|pathmask)>>i)&1)
  for name in remaining:
   for mask,cells in available[name]:
    if (mask>>target)&1 and not mask&occupied:
     fill(occupied|mask,[n for n in remaining if n!=name],chosen+[(name,cells)])
 fill(0,list(SHAPES),[])
path_keys={tuple(map(tuple,s['path'])) for s in solutions}
print('Solutions',len(solutions),'distinct paths',len(path_keys))
clues=[]
for k in [1,2,3]:
 for cells in combinations([(x,y) for y in range(5) for x in range(5) if (x,y) not in [(0,0),(4,4)]],k):
  matches=[s for s in solutions if set(cells)<=set(map(tuple,s['path']))]
  if matches:
   pk={tuple(map(tuple,s['path'])) for s in matches}
   if len(matches)<=4:clues.append({'clues':cells,'solution_count':len(matches),'distinct_paths':len(pk),'example':matches[0]})
clues.sort(key=lambda x:(len(x['clues']),x['solution_count']))
(P/'search.json').write_text(json.dumps({'board_size':N,'shapes':SHAPES,'allowed_rotations':True,'allowed_reflections':True,'all_solution_count':len(solutions),'distinct_path_count':len(path_keys),'solutions':solutions,'small_clue_sets':clues},indent=2)+'\n')
print(json.dumps(clues[:8],ensure_ascii=False))
