"""Rear upper-guide envelope only; not a buildable or escape-validated assembly.
A gravity-biased carriage is the proposed return principle, not verified behavior.
"""
import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part
V=A.Vector;P=Path(__file__).resolve().parent;D=A.newDocument('RearCartridgeEnvelope')
parts=[]
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def cyl(r,l,x,y,z):return Part.makeCylinder(r,l,V(x,y,z),V(0,1,0))
def ann(r,inner,l,x,y,z):return cyl(r,l,x,y,z).cut(cyl(inner,l,x,y,z))
def add(name,shape,role):
 o=D.addObject('Part::Feature',name);o.Shape=shape;o.addProperty('App::PropertyString','ConceptRole');o.ConceptRole=role;parts.append(o);return o
# Rear-only rail and stop envelopes, 2 mm total vertical carriage travel.
# Arbitrary guide clearances are not fabrication tolerances.
add('Rear_mount_plate',box(-16,68.25,342,32,5,40),'Unspecified attachment to a rear gantry; stiffness and mounting not designed')
for x in [-14,10]:add('Side_rail_'+str(x),box(x,58,349,4,12,26),'Geometric guide envelope, not a selected sliding bearing')
for x in [-10,7]:add('Front_keeper_'+str(x),box(x,58,355,3,1.75,14),'Keeps carriage from moving forward in this nominal envelope; not ring capture')
lo=add('Lower_geometric_stop',box(-10,58,352,20,12,3),'Nominal lower limit delta=-1 mm')
hi=add('Upper_geometric_stop',box(-10,58,369,20,12,3),'Nominal upper limit delta=+1 mm')
carriage=add('Sliding_carriage',box(-9.5,60,356,19,8,12),'Gravity-biased return candidate; force, friction and sticking unvalidated')
carriage.addProperty('App::PropertyDistance','NominalTravelEachWay');carriage.NominalTravelEachWay=1
# Current roller unchanged: root radius9/lip11, 4.4mm slot, .2 sidegap.
y=-50.;z=362.;g=.2;slot=4+2*g;w=slot+5.6
add('Groove_root_sleeve',ann(9,2,slot,0,y-slot/2,z),'Nominal running surface; no bearing insert specified')
add('Front_lip',ann(11,2,2.8,0,y-w/2,z),'2mm radial overhang; ring escape NOT established')
add('Rear_lip',ann(11,2,2.8,0,y+slot/2,z),'Axial contact may carry pitch moment and introduce sliding drag')
add('Axle_envelope',cyl(1.8,w+3,0,y-w/2-1.5,z),'Envelope only; no fit, material, bearing or capacity selection')
add('Front_retention_envelope',ann(3,1.8,1,0,y-w/2-1.5,z),'Placeholder collar; fastening method unresolved')
add('Long_rear_post',cyl(3,104.5,0,-44.5,z),'Long cantilever is not stiffness-validated')
# Axial spacer gap is independent of vertical travel, shown in custom property.
D.addObject('App::FeaturePython','Parameters');par=D.getObject('Parameters');par.addProperty('App::PropertyLength','NominalGrooveSideGap');par.NominalGrooveSideGap=.2;par.addProperty('App::PropertyString','Status');par.Status='Geometry-only. Adjustment fasteners, guide bearings, return force and ring capture unresolved.'
# Exact local stop checks, not a full mechanism collision analysis.
checks=[]
for delta in [-1.1,-1.,-.7516,0.,.7488,1.,1.1]:
 s=carriage.Shape.copy();s.translate(V(0,0,delta));overlap=s.common(lo.Shape).Volume+s.common(hi.Shape).Volume
 checks.append({'delta_mm':delta,'stop_overlap_mm3':overlap})
 if abs(delta)<=1:assert overlap<1e-6
 else:assert overlap>0
assert all(o.Shape.isValid() for o in parts)
D.recompute();D.saveAs(str(P/'rear_cartridge_envelope.FCStd'))
result={'parts':len(parts),'valid_solids':True,'stop_checks':checks,'warning':'Stops capture carriage travel only. No continuous 3D ring-retention proof; no selected bearing, spring, stiffness or hardware assembly. Axial spacer setting and radial travel are independent geometrically, not a finished adjustable assembly.'}
(P/'cartridge_geometry.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
