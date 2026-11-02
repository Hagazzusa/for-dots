"""Analytic triangle overlap + island-boundary gutter validation, no renderer required."""
import json,math,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];d=json.loads((ROOT/'qa/wood_uv_raw.json').read_text());polys=d['polygons'];tri=d['triangles'];res=d['resolution'];EPS=1e-10

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(v):return abs(sum(v[i][0]*v[(i+1)%len(v)][1]-v[(i+1)%len(v)][0]*v[i][1] for i in range(len(v))))*.5 if len(v)>2 else 0

def intersect(poly,clip):
 out=list(poly);sign=1 if cross(*clip)>0 else -1
 for j in range(3):
  a,b=clip[j],clip[(j+1)%3];inp=out;out=[]
  if not inp:break
  for i,p in enumerate(inp):
   q=inp[(i+1)%len(inp)];dp=sign*cross(a,b,p);dq=sign*cross(a,b,q);ip=dp>=-EPS;iq=dq>=-EPS
   if ip:out.append(p)
   if ip!=iq:
    t=dp/(dp-dq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return area(out)
# Connect faces only across the same mesh edge AND continuous UV edge.
parent=list(range(len(polys)))
def find(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
edges={}
for i,p in enumerate(polys):
 for j in range(len(p['vertices'])):
  k=(j+1)%len(p['vertices']);a=(p['vertices'][j],*map(lambda z:round(z,7),p['uv'][j]));b=(p['vertices'][k],*map(lambda z:round(z,7),p['uv'][k]));key=tuple(sorted((a,b)))
  if key in edges:
   other=edges[key][0];parent[find(i)]=find(other);edges[key][3]+=1
  else:edges[key]=[i,p['uv'][j],p['uv'][k],1]
# Spatial bins prune analytic triangle tests, with exact intersection areas thereafter.
grid=collections.defaultdict(list);overlaps=[];tested=set()
for i,t in enumerate(tri):
 u=t['uv'];xs=[x[0] for x in u];ys=[x[1] for x in u];keys=[(x,y) for x in range(int(min(xs)*64),int(max(xs)*64)+1) for y in range(int(min(ys)*64),int(max(ys)*64)+1)]
 candidates=set(j for k in keys for j in grid[k])
 for j in candidates:
  ar=intersect(u,tri[j]['uv'])
  if ar>1e-9:overlaps.append({'triangles':[i,j],'area':ar})
 for k in keys:grid[k].append(i)
# Boundary segment minimum distance between distinct UV islands.
def pd(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def sd(a,b,c,d):return min(pd(a,c,d),pd(b,c,d),pd(c,a,b),pd(d,a,b))
boundaries=[(find(i),a,b) for i,a,b,n in edges.values() if n==1];eg=collections.defaultdict(list);gap=1.0
for i,(island,a,b) in enumerate(boundaries):
 keys=[(x,y) for x in range(int((min(a[0],b[0])-.025)*64),int((max(a[0],b[0])+.025)*64)+1) for y in range(int((min(a[1],b[1])-.025)*64),int((max(a[1],b[1])+.025)*64)+1)]
 for j in set(j for k in keys for j in eg[k]):
  other,c,e=boundaries[j]
  if other!=island:gap=min(gap,sd(a,b,c,e))
 for k in keys:eg[k].append(i)
uvarea=sum(area(t['uv']) for t in tri);worldarea=sum(p['area'] for p in polys);invalid=sum(any(x < -1e-6 or x>1+1e-6 for p in t['uv'] for x in p) for t in tri);degenerate=sum(area(t['uv'])<1e-12 for t in tri)
islands=collections.defaultdict(lambda:{'uv_area':0,'surface_area':0})
for i,p in enumerate(polys):islands[find(i)]['uv_area']+=area(p['uv']);islands[find(i)]['surface_area']+=p['area']
densities=sorted(res*math.sqrt(v['uv_area']/v['surface_area']) for v in islands.values() if v['surface_area']>1e-12)
report={'resolution':res,'triangles':len(tri),'uv_islands':len(islands),'coverage_fraction':uvarea,'wood_surface_area_m2':worldarea,'invalid_uv_triangles':invalid,'degenerate_uv_triangles':degenerate,'positive_area_overlaps':len(overlaps),'largest_overlap_area':max((x['area'] for x in overlaps),default=0),'minimum_island_gap_pixels':gap*res,'texels_per_metre':{'area_average':res*math.sqrt(uvarea/worldarea),'min':min(densities),'median':densities[len(densities)//2],'max':max(densities)},'overlap_tolerance_uv_area':1e-9,'pass':not invalid and not degenerate and not overlaps and gap*res>=7.9}
(ROOT/'qa/wood_uv_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['pass']
