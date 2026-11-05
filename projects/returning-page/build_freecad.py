"""Native editable FreeCAD feature tree. /usr/bin/python3; FreeCAD 1.0."""
import FreeCAD as A, Part, MeshPart
import json, math, hashlib
from pathlib import Path
R=Path(__file__).resolve().parent; O=R/'cad'; O.mkdir(exist_ok=True)
d=A.newDocument('Returning_Page')
b=d.addObject('Part::Box','Blank'); b.Length=25; b.Width=90; b.Height=.7
d.recompute()
f=d.addObject('Part::Fillet','Rounded_Corners'); f.Base=b
f.Edges=[(i+1,3,3) for i,e in enumerate(b.Shape.Edges) if abs(e.Length-.7)<1e-6]; d.recompute()
# A single softly cornered window: the quiet rectangle of a shelter seen from home.
w=d.addObject('Part::Box','Shelter_Window'); w.Length=15; w.Width=13; w.Height=3; w.Placement.Base=A.Vector(5,63,-1)
d.recompute(); wf=d.addObject('Part::Fillet','Window_Corners'); wf.Base=w
wf.Edges=[(i+1,1.5,1.5) for i,e in enumerate(w.Shape.Edges) if abs(e.Length-3)<1e-6]; d.recompute()
c=d.addObject('Part::Cut','Window_Cut'); c.Base=f; c.Tool=wf
h=d.addObject('Part::Cylinder','Thread_Hole'); h.Radius=1.4; h.Height=3; h.Placement.Base=A.Vector(12.5,83,-1)
d.recompute(); cut=d.addObject('Part::Cut','Hole_Cut'); cut.Base=c; cut.Tool=h; d.recompute()
fin=d.addObject('Part::Fillet','Brass_Bookmark'); fin.Base=cut
fin.Edges=[(i+1,.14,.14) for i,e in enumerate(cut.Shape.Edges) if e.BoundBox.ZLength<1e-6]; d.recompute()
s=fin.Shape; assert s.isValid() and len(s.Solids)==1 and s.Volume>0; s.check(True)
for obj in d.Objects: obj.Visibility=False
fin.Visibility=True
d.saveAs(str(O/'Returning_Page.FCStd')); Part.export([fin],str(O/'Returning_Page.step'))
m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.08,Relative=False)
v,t=m.Topology; vs=[[float(p.x),float(p.y),float(p.z)] for p in v]; fs=[list(f) for f in t]
assert all(math.isfinite(x) for v in vs for x in v)
(O/'bookmark_mesh.json').write_text(json.dumps({'units':'mm','vertices':vs,'faces':fs},separators=(',',':'))+'\n')
step=Part.Shape(); step.read(str(O/'Returning_Page.step'))
assert step.isValid() and len(step.Solids)==1
r={'valid_solid':True,'solid_count':1,'dimensions_mm':[25,90,.7],'outer_corner_radius_mm':3,'edge_radius_mm':.14,'window_mm':[15,13],'window_radius_mm':1.5,'thread_hole_diameter_mm':2.8,'volume_mm3':s.Volume,'step_volume_error_mm3':abs(step.Volume-s.Volume),'mesh_vertices':len(vs),'mesh_triangles':len(fs),'finite_vertices':True}
A.closeDocument(d.Name); d=A.openDocument(str(O/'Returning_Page.FCStd')); assert d.Brass_Bookmark.Shape.isValid()
old=d.Brass_Bookmark.Shape.Volume; d.Blank.Width=92; d.recompute(); assert d.Brass_Bookmark.Shape.isValid() and d.Brass_Bookmark.Shape.Volume>old
r['reopened_native_parameter_edit_verified']='Blank.Width 90 to 92 mm increases volume; original saved at 90 mm'; A.closeDocument(d.Name)
(O/'validation.json').write_text(json.dumps(r,indent=2)+'\n'); print(r)
