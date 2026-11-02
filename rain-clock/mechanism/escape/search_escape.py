"""Finite grid search of outer-track rigid poses; no absence-of-escape proof.
FreeCAD/OpenCascade exact solid intersections apply to the polygonized BRep,
not to a manufactured part or an exact analytic three-lobe surface.
"""
import sys,os,json,math,time
from pathlib import Path
from collections import deque
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part,numpy as np
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent;V=A.Vector
SEGMENTS=720;AMP=.25;R=143.;INNER=135.;PHASE=math.pi/3
# Theta measured from upward +Z.
a=np.arange(SEGMENTS)*2*np.pi/SEGMENTS;rad=R+AMP*np.cos(3*(a-PHASE));vertices=np.column_stack((rad*np.sin(a),rad*np.cos(a)))
seg=np.roll(vertices,-1,axis=0)-vertices;ss=(seg*seg).sum(axis=1)
angles=np.arange(3)*2*math.pi/3;normals=np.column_stack((np.sin(angles),np.cos(angles)))
def gap2(q):
 c=q[:2];centers=152*normals;centers[0,1]+=q[2];out=[]
 for cc in centers:
  w=cc-c-vertices;t=np.clip((w*seg).sum(axis=1)/ss,0,1);ds=w-t[:,None]*seg;out.append(float(np.sqrt((ds*ds).sum(axis=1).min())-9))
 return out
sol=least_squares(gap2,[.0001,-.5,-.75],bounds=([-1,-1,-1],[1,1,1]),ftol=1e-13,xtol=1e-13,gtol=1e-13)
assert max(abs(np.array(gap2(sol.x))))<1e-8
CX,CZ,D0=map(float,sol.x)
wire=Part.makePolygon([V(float(x),-2,float(z)) for x,z in vertices]+[V(float(vertices[0,0]),-2,float(vertices[0,1]))]);track=Part.Face(wire).extrude(V(0,4,0));track=track.cut(Part.makeCylinder(INNER,4,V(0,-2,0),V(0,1,0)))
assert track.isValid()
def wheel(x,z):
 c=lambda r,h,y:Part.makeCylinder(r,h,V(x,y,z),V(0,1,0))
 return c(9,10,-5).fuse(c(11,2.8,-5)).fuse(c(11,2.8,2.2)).cut(c(2,10,-5))
fixed=[wheel(float(n[0]*152),float(n[1]*152)) for n in normals[1:]]
upper=wheel(0,152)
# Save exact modeled solids at the initial adverse phase and stuck follower.
doc=A.newDocument('EscapeSearchNominalSolids')
for name,sh in [('Outer_lobed_track_polygon720',track),('Lower_right',fixed[0]),('Lower_left',fixed[1]),('Upper_outward_stuck',upper)]:
 o=doc.addObject('Part::Feature',name);o.Shape=sh
 if name.startswith('Outer'):o.Placement.Base=V(CX,0,CZ)
 if name.startswith('Upper'):o.Placement.Base=V(0,0,1)
 o.addProperty('App::PropertyString','Scope');o.Scope='Search subset: track and three guides only; not a complete sculpture or hardware assembly'
doc.recompute();doc.saveAs(str(P/'escape_search_solids.FCStd'))
# Finite domain and axis-adjacent graph. All coordinates relative to solved pose.
STEPS=(.05,.25,.05) # axial mm, vertical mm, pitch degrees
LO=(-160,-2,-120);HI=(160,10,120) # +/-8mm axial, -.5..2.5mm lift, +/-6deg pitch
VOLUME_FREE=1e-9;VOLUME_COLLISION=1e-5
results=[]
for mode in ['translation_following_approx','outward_stuck']:
 start=time.monotonic();cache={};parents={};q=deque();free=[];blocked=[];ambiguous=[];hardstop=[];goal=None;edge_midpoints=0
 def classify_coords(coords):
  y,z,pitch=coords;delta=D0+z if mode=='translation_following_approx' else 1.
  if delta < -1-1e-9 or delta > 1+1e-9:return ('travel_limit',None,None)
  s=track.copy();s.rotate(V(0,0,0),V(1,0,0),pitch);s.translate(V(CX,y,CZ+z))
  up=upper.copy();up.translate(V(0,0,delta));vols=[]
  for obs in [up,*fixed]:
   v=float(s.common(obs).Volume);vols.append(v)
   if v>VOLUME_COLLISION:return ('collision',v,None)
   if v>VOLUME_FREE:return ('near_contact_uncertain',v,None)
  endpoint=bool(s.BoundBox.YMax < -5.1 or s.BoundBox.YMin > 5.1)
  return ('free',max(vols),endpoint)
 def classify(idx):
  if idx not in cache:cache[idx]=classify_coords(tuple(i*h for i,h in zip(idx,STEPS)))
  return cache[idx]
 origin=(0,0,0);assert classify(origin)[0]=='free',(mode,classify(origin));q.append(origin);parents[origin]=None
 while q:
  cur=q.popleft();free.append(cur)
  if classify(cur)[2]:goal=cur;break
  for dim in range(3):
   for direction in [-1,1]:
    nxt=list(cur);nxt[dim]+=direction;nxt=tuple(nxt)
    if any(i<lo or i>hi for i,lo,hi in zip(nxt,LO,HI)) or nxt in parents:continue
    status,vol,end=classify(nxt)
    if status!='free':continue
    # Check midpoint too. This still does not certify the continuous edge.
    mid=tuple((a+b)*h/2 for a,b,h in zip(cur,nxt,STEPS));m=classify_coords(mid);edge_midpoints+=1
    if m[0]!='free':continue
    parents[nxt]=cur;q.append(nxt)
  if len(free)%100==0:print(mode,'reachable',len(free),'tested',len(cache),'seconds',round(time.monotonic()-start,1),flush=True)
 for idx,val in cache.items():
  row={'index':idx,'pose':[i*h for i,h in zip(idx,STEPS)],'status':val[0],'intersection_mm3':val[1]}
  if val[0]=='collision':blocked.append(row)
  elif val[0]=='near_contact_uncertain':ambiguous.append(row)
  elif val[0]=='travel_limit':hardstop.append(row)
 path=[]
 if goal is not None:
  at=goal
  while at is not None:path.append(at);at=parents[at]
  path.reverse()
 result={'mode':mode,'outcome':'sampled_track_only_path_found_requires_full_assembly_and_continuous_validation' if goal else 'inconclusive_no_endpoint_in_reachable_sampled_component','seconds':time.monotonic()-start,'unique_grid_poses_tested':len(cache),'reachable_grid_poses':len(free),'checked_edge_midpoints':edge_midpoints,'collision_poses':len(blocked),'uncertain_poses':len(ambiguous),'travel_limited_poses':len(hardstop),'reachable_poses':[[i*h for i,h in zip(idx,STEPS)] for idx in free],'sampled_path':[[i*h for i,h in zip(idx,STEPS)] for idx in path],'blocked_poses':blocked,'uncertain_details':ambiguous}
 results.append(result);print(json.dumps({k:v for k,v in result.items() if k not in ['reachable_poses','sampled_path','blocked_poses','uncertain_details']}),flush=True)
 (P/'progress_results.json').write_text(json.dumps(results,indent=2))
output={'status':'Bounded sampled investigation; neither mode can prove absence of a continuous escape path.','solids':'4mm extruded polygon720 outer profile R143 + .25*cos(3*(theta-pi/3)), inner circle R135; guide root R9, lip R11, width10, groove4.4. OpenCascade intersections are exact for these modeled BReps subject to numeric tolerances; smooth lobed shape is approximated.','initial_pose':{'center_x_mm':CX,'center_z_mm':CZ,'closed_follower_shift_mm':D0,'shape_phase_deg':60},'domain':{'axial_Y_mm':[-8,8],'vertical_lift_mm':[-.5,2.5],'pitch_X_deg':[-6,6],'steps':STEPS,'fixed_DOF':['horizontal X translation','roll about Z','in-plane rotation about Y / shape phase'],'neighbors':'six axis-adjacent neighbors; midpoint checked for each admitted edge'},'tracking_assumption':'Approximate translation following: upper shift = initial closed shift + vertical lift. Pitch-dependent tracking, contact loss and forces are not solved. Hard stops +/-1mm. This is a restrictive kinematic assumption, not real follower dynamics.','stuck_assumption':'Upper follower fixed at +1mm; lower guides fixed.','collision_classification':{'free_volume_at_most_mm3':VOLUME_FREE,'blocked_volume_above_mm3':VOLUME_COLLISION,'intermediate':'uncertain and excluded from reachable component'},'escape_endpoint':'Track Y bounds fully beyond guide flange slab by .1mm: ymax<−5.1 or ymin>+5.1. This is only a track-subset endpoint.','omitted':['beads/pins/tab and their collisions','posts/frame/rear carriage','elastic deformation and friction','gravity and manual force','continuous edge certification','other pose domains and coupled rotations'],'results':results}
(P/'results.json').write_text(json.dumps(output,indent=2));print('SEARCH_COMPLETE',flush=True)
