"""Three virtual groove-width coupons. No assembly or fit recommendation."""
from pathlib import Path
import sys,json
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part
P=Path(__file__).resolve().parent;D=A.newDocument('GrooveSideGapVariants');v=A.Vector
rows=[]
for i,g in enumerate([.2,.4,.6]):
 x=i*35;groove=4+2*g;width=groove+5.6
 def cyl(r,length,y):return Part.makeCylinder(r,length,v(x,y,0),v(0,1,0))
 shape=cyl(9,width,-width/2).fuse(cyl(11,2.8,-width/2)).fuse(cyl(11,2.8,groove/2)).cut(cyl(2,width,-width/2))
 o=D.addObject('Part::Feature','Groove_'+str(g).replace('.','_'));o.Shape=shape;o.addProperty('App::PropertyLength','NominalSideGap');o.NominalSideGap=g;o.addProperty('App::PropertyString','Status');o.Status='Hypothetical envelope, not manufacturing tolerance'
 # The track coupon touches the groove root at x=9; lips enclose its Y thickness.
 t=D.addObject('Part::Feature','Track_coupon_'+str(i));t.Shape=Part.makeBox(8,4,4,v(x+9,-2,-2))
 assert o.Shape.isValid() and t.Shape.isValid()
 assert o.Shape.common(t.Shape).Volume<1e-6
 rows.append({'sidegap_mm':g,'groove_width_mm':groove,'roller_total_width_mm':width,'lip_width_mm':2.8,'nominal_bead_to_front_lip_remaining_mm':4.4-(width-10)/2,'note':'Unchanged root/lip radii; wider axial spacer envelope only. Contact is approximate local coupon, not ring dynamics.'})
D.recompute();D.saveAs(str(P/'groove_variants.FCStd'));(P/'groove_variants.json').write_text(json.dumps(rows,indent=2));print(rows)
