"""Headless FreeCAD concept in mm; not fabrication drawings.
Run with /usr/bin/python3. Original study stays unchanged.
"""
import sys, math, json
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A, Part
V=A.Vector
ROOT=Path(__file__).resolve().parent
D=A.newDocument('RainClockManualStudy')
parts=[]
def add(name,shape,color,group='fixed'):
 o=D.addObject('Part::Feature',name);o.Label=name.replace('_',' ');o.Shape=shape
 o.addProperty('App::PropertyString','StudyRole');o.StudyRole=group
 o.addProperty('App::PropertyVector','PreviewColor');o.PreviewColor=V(*color)
 parts.append((o,color,group));return o
ink=(.025,.065,.075);brass=(.56,.34,.13);teal=(.11,.48,.49);amber=(.95,.42,.12);gray=(.13,.17,.18);red=(.65,.16,.09)
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def cyl(r,l,x,y,z):return Part.makeCylinder(r,l,V(x,y,z),V(0,1,0))
def ann(r1,r0,l,x,y,z):return cyl(r1,l,x,y,z).cut(cyl(r0,l,x,y,z))
add('Widened_base_390x210',box(-195,-130,0,390,210,40),gray)
add('Deck',box(-180,-120,40,360,190,9),ink)
add('Fixed_shelter',box(-56,8.5,77.5,112,29,135),ink)
add('Warm_pane_unpowered_placeholder',box(-39,-1,94,78,4,102),amber)
add('Canopy',box(-67,-32,212.5,134,72,9),brass)
add('Sill',box(-65,-30.5,84,130,55,8),brass)
add('Fixed_outer_frame',ann(169.5,156.5,15,0,10.5,210),ink)
for x in [-162,162]:add('Frame_stem_'+str(x),box(x-4.5,13.5,49,9,9,161),brass)
# Back rails support roller posts without crossing the shelter canopy.
for x in [-76,-60.5,121,152]:
 add('Rear_column_'+str(x).replace('.','_'),box(x-3,52,49,6,6,300 if x<0 else 161),ink)
roller_objects=[]
for j,(r,track_y,n) in enumerate([(139,-50,11),(108,-80,8)]):
 label='Outer' if j==0 else 'Inner';bead_y=track_y-14
 add(label+'_running_track',ann(r+4,r-4,4,0,track_y-2,210),brass,label)
 for k in range(n):
  a=math.tau*k/n+.2*j;x=r*math.cos(a);z=210+r*math.sin(a)
  sphere=Part.makeSphere(1);m=A.Matrix();m.scale(5.8,4.6,10.5);sphere=sphere.transformGeometry(m);sphere.translate(V(x,bead_y,z))
  add(label+'_bead_%02d'%k,sphere,teal if k%3 else brass,label)
  add(label+'_bead_pin_%02d'%k,cyl(1,14,x,bead_y,z),brass,label)
 # Rounded manual tab; only manual oscillation, no hidden actuator.
 tab=box(r-3,bead_y-14,204,6,14,12)
 add(label+'_manual_tab',tab,teal,label)
 for k,degrees in enumerate([0,120,240]):
  a=math.radians(degrees);x=(r+13)*math.cos(a);z=210+(r+13)*math.sin(a)
  # Groove root R9; retaining lips R11; 4.4 mm slot around 4 mm track.
  wheel=cyl(9,10,x,track_y-5,z).fuse(cyl(11,2.8,x,track_y-5,z)).fuse(cyl(11,2.8,x,track_y+2.2,z)).cut(cyl(2,10,x,track_y-5,z))
  wheel_obj=add(label+'_guide_roller_%d'%k,wheel,gray);roller_objects.append((label,wheel_obj))
  add(label+'_axle_%d'%k,cyl(1.8,12,x,track_y-6,z),brass)
  add(label+'_support_post_%d'%k,cyl(3,55-(track_y+5),x,track_y+5,z),ink)
  # Adjustable rear slot is a visible concept carrier, not a bearing specification.
  carrier=box(x-9,50,z-6,18,10,12).cut(box(x-5,49,z-1.5,10,12,3))
  add(label+'_slotted_carrier_%d'%k,carrier,red if k==0 else ink)
# Geometry and representative collision checks (not a certified assembly analysis).
assert all(o.Shape.isValid() and not o.Shape.isNull() for o,_,_ in parts)
fixed_shelter=[o for o,c,g in parts if o.Name in ['Fixed_shelter','Canopy','Sill','Warm_pane_unpowered_placeholder']]
# Rotating shapes evaluated at original animation samples. Fixed rollers remain stationary.
# Rotation is around Y: the Y extents are invariant for the full motion cycle.
# Positive disjoint Y intervals prove shelter separation at all angles, not just sampled frames.
collisions=[];minimum=1e9;pair=''
for o,c,g in parts:
 if g not in ('Outer','Inner'):continue
 for fixed in fixed_shelter:
  gap=fixed.Shape.BoundBox.YMin-o.Shape.BoundBox.YMax
  assert gap>0, (o.Name,fixed.Name,gap)
  if gap<minimum:minimum=gap;pair=o.Name+' / '+fixed.Name
# Reconstruction of the old un-beveled sill and smooth bead at original frame 25.
s=Part.makeSphere(1);m=A.Matrix();m.scale(5.8,4.6,10.5);s=s.transformGeometry(m)
a=6/8*math.tau+.2;s.translate(V(112*math.cos(a),-19,210+112*math.sin(a)))
original_overlap=s.common(box(-65,-30.5,84,130,55,8)).Volume
# Purposeful running contact: ring touches groove root but must not overlap roller solid.
contact=[]
for label,roller in roller_objects:
 ring=next(o for o,c,g in parts if o.Name==label+'_running_track')
 contact.append({'pair':ring.Name+'/'+roller.Name,'overlap_mm3':ring.Shape.common(roller.Shape).Volume,'distance_mm':ring.Shape.distToShape(roller.Shape)[0]})
assert not collisions
assert all(x['overlap_mm3']<1e-6 for x in contact)
D.recompute();D.saveAs(str(ROOT/'rain_clock_manual.FCStd'))
# Mesh exchange for a separate headless Blender preview, no imported assets.
mesh=[]
for o,c,g in parts:
 vertices,faces=o.Shape.tessellate(.4)
 mesh.append({'name':o.Name,'color':c,'group':g,'vertices':[list(v) for v in vertices],'faces':faces})
(ROOT/'preview_mesh.json').write_text(json.dumps(mesh))
result={'units':'mm; invented study scale 100 mm per original Blender unit','parts':len(parts),'valid_solids':True,'shelter_separation_proof':'All moving shapes are in disjoint Y intervals from all shelter solids; Y rotation preserves this for every angle','minimum_full_cycle_shelter_Y_gap_mm':minimum,'original_nominal_bead6_sill_overlap_mm3':original_overlap,'minimum_pair':pair,'ring_roller_contacts':contact,'analytic_conservative_clearances_mm':{'bead_back_to_roller_front':4.4,'bead_pin_to_roller_lip_radial':1.0,'outer_bead_sweep_to_inner_support_post':4.5,'track_axial_slot_each_side':.2,'inner_bead_back_to_outer_track_front':37.4,'rear_columns_to_canopy':12,'outer_posts_to_fixed_frame_inner_edge':1.5},'limits':'No tolerance stack, friction, stiffness, hand force, tipping, wear or safety validation. Not all pairs of solids checked. Roller bearings and retention are envelope placeholders.'}
(ROOT/'geometry_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
