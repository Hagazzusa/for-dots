"""Rear-axle silhouette study. Not bearing sizing, stiffness or manufacturing design."""
import sys,math,json
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part
V=A.Vector;P=Path(__file__).resolve().parent
source=A.openDocument(str(P.parent/'rain_clock_manual.FCStd'));D=A.newDocument('RearAxleVisualAlternative')
parts=[];ink=(.025,.065,.075);brass=(.56,.34,.13);teal=(.11,.48,.49);gray=(.13,.17,.18);amber=(.95,.42,.12)
def add(name,shape,color,role='fixed'):
 o=D.addObject('Part::Feature',name);o.Shape=shape;o.addProperty('App::PropertyString','ConceptRole');o.ConceptRole=role;parts.append((o,color,role));return o
def cyl(r,length,x,y,z):return Part.makeCylinder(r,length,V(x,y,z),V(0,1,0))
def ann(r,ri,l,x,y,z):return cyl(r,l,x,y,z).cut(cyl(ri,l,x,y,z))
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def rod(a,b,r):
 a=V(*a);b=V(*b);d=b-a;return Part.makeCylinder(r,d.Length,a,d.normalize())
for o in source.Objects:
 name=o.Name;role=o.StudyRole
 if role in ['Outer','Inner'] or name in ['Deck','Fixed_shelter','Warm_pane_unpowered_placeholder','Canopy','Sill','Fixed_outer_frame'] or name.startswith('Frame_stem_'):
  c=tuple(o.PreviewColor);add(name,o.Shape.copy(),c,role)
add('Base_rear_depth_plus10',box(-195,-130,0,390,220,40),gray)
add('Rear_axis_upright',box(-10,82,49,20,8,171),ink)
add('Stationary_common_shaft',cyl(3,49.5,0,40.5,210),brass)
spokes=[];bridges=[];hubs=[]
for label,r,plane,track_y,half_angle in [('Outer',139,47,-50,3),('Inner',108,64,-80,45)]:
 hub=add(label+'_independent_hub',ann(10,6.5,10,0,plane-5,210),ink,label);hubs.append(hub)
 for y in [plane-4,plane+1]:add(label+'_bearing_envelope_'+str(y),ann(6.5,3.5,3,0,y,210),gray,label)
 for y in [plane-6.5,plane+5.5]:add(label+'_axial_collar_envelope_'+str(y),ann(5,3,1,0,y,210),brass)
 for k,s in enumerate([-1,1]):
  t=math.radians(s*half_angle);direction=(math.sin(t),-math.cos(t))
  start=(9*direction[0],plane,210+9*direction[1]);end=(r*direction[0],plane,210+r*direction[1])
  spokes.append(add(label+'_downward_spoke_'+str(k),rod(start,end,1.6),brass,label))
  bridges.append(add(label+'_forward_bridge_'+str(k),rod(end,(end[0],track_y,end[2]),2),brass,label))
assert all(o.Shape.isValid() for o,c,g in parts)
window=[o for o,c,g in parts if o.Name in ['Fixed_shelter','Warm_pane_unpowered_placeholder','Canopy','Sill']]
# Exact representative angular sweep: bridges/spokes/hubs against fixed window solids.
collision=[];tests=0;min_gap=1e9;min_pair=''
for label,amp in [('Outer',.15),('Inner',.19)]:
 supports=[o for o,c,g in parts if g==label and any(x in o.Name for x in ['_spoke_','_bridge_','_independent_hub'])]
 for k in range(17):
  deg=math.degrees(-amp+2*amp*k/16)
  for o in supports:
   s=o.Shape.copy();s.rotate(V(0,0,210),V(0,1,0),deg)
   for w in window:
    tests+=1;v=s.common(w.Shape).Volume
    if v>1e-6:collision.append([label,k,o.Name,w.Name,v])
    d=s.distToShape(w.Shape)[0]
    if d<min_gap:min_gap=d;min_pair=o.Name+'/'+w.Name
assert not collision,collision
# Ray/box visibility samples: only fixed window, not projected area or full-scene visibility.
bounds=[o.Shape.BoundBox for o in window]
def hit_window(point,view):
 for b in bounds:
  lo=[b.XMin,b.YMin,b.ZMin];hi=[b.XMax,b.YMax,b.ZMax];near=0.;far=1e8
  for i in range(3):
   if abs(view[i])<1e-12:
    if point[i]<lo[i] or point[i]>hi[i]:near=1;far=0;break
   else:
    a=(lo[i]-point[i])/view[i];c=(hi[i]-point[i])/view[i];near=max(near,min(a,c));far=min(far,max(a,c))
  if far>=near and far>1e-7:return True
 return False
visibility=[]
for label,r,plane,angle in [('Outer',139,47,3),('Inner',108,64,45)]:
 for view_name,view in [('Front',(0,-1,0)),('Three_quarter',(5,-10,3.4))]:
  for kind in ['hub_surface','spoke_centerlines']:
   pts=[]
   if kind=='hub_surface':
    for y in [plane-5,plane+5]:
     for i in range(72):
      a=i*math.tau/72;pts.append((10*math.cos(a),y,210+10*math.sin(a)))
   else:
    for sign in [-1,1]:
     a=math.radians(angle*sign)
     for j in range(51):
      t=9+(r-9)*j/50;pts.append((t*math.sin(a),plane,210-t*math.cos(a)))
   hidden=sum(hit_window(p,view) for p in pts)
   visibility.append({'ring':label,'view':view_name,'sample_type':kind,'hidden_points':hidden,'points':len(pts),'caveat':'Nominal zero-angle pose; sampled-point count, NOT projected area; window bounding boxes only'})
D.recompute();D.saveAs(str(P/'rear_axle_alternative.FCStd'))
mesh=[]
for o,c,g in parts:
 v,f=o.Shape.tessellate(.4);mesh.append({'name':o.Name,'color':c,'group':g,'vertices':[list(x) for x in v],'faces':f})
(P/'preview_mesh.json').write_text(json.dumps(mesh))
r={'parts':len(parts),'all_solids_valid':True,'exact_support_window_tests':tests,'sampled_angles_each_ring':17,'window_intersections':collision,'minimum_tested_support_window_distance_mm':min_gap,'minimum_pair':min_pair,'visibility_samples':visibility,'dimensions':{'hub_centers_Y_mm':[47,64],'hub_outer_radius_mm':10,'shaft_radius_envelope_mm':3,'outer_spoke_halfangle_deg':3,'inner_spoke_halfangle_deg':45,'forward_bridge_lengths_mm':[97,144],'base_depth_mm':220},'limits':'No bearings selected; gaps are geometric placeholders, not fits. Spoke/shaft stiffness, axial retention fastening, drag, force, torque, assembly access and full cross-part sweep unvalidated. Front hubs are hidden, but quarter-view visibility is checked rather than assumed.'}
(P/'geometry_comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
