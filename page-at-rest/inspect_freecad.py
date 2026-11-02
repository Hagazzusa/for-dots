"""Reopen CAD, exercise two native parameters in memory, then restore them.
The input FCStd/STEP are never saved or overwritten. Only the JSON report is
written. Run serially with the other CPU jobs using system FreeCAD Python.
"""
from pathlib import Path
import hashlib,json,math
import FreeCAD as App
import Part
ROOT=Path(__file__).resolve().parent
source=ROOT/'cad/A_Page_at_Rest.FCStd'
before=hashlib.sha256(source.read_bytes()).hexdigest()
doc=App.openDocument(str(source));doc.recompute()
names=['Walnut_Base','Left_Brass_Cradle','Right_Brass_Cradle']
objects=[doc.getObject(n) for n in names]
assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in objects)
volumes={o.Name:o.Shape.Volume for o in objects}
ellipse=doc.getObject('Base_Ellipse');old=float(ellipse.MajorRadius.Value)
ellipse.MajorRadius=old+1;doc.recompute()
changed_base=doc.getObject('Walnut_Base').Shape.Volume
assert doc.getObject('Walnut_Base').Shape.isValid() and changed_base>volumes['Walnut_Base']
ellipse.MajorRadius=old;doc.recompute()
section=doc.getObject('Left_Stem_Loft_Section_00');old_radius=float(section.Radius.Value)
section.Radius=old_radius+.2;doc.recompute()
changed_support=doc.getObject('Left_Brass_Cradle').Shape.Volume
assert doc.getObject('Left_Brass_Cradle').Shape.isValid() and changed_support>volumes['Left_Brass_Cradle']
section.Radius=old_radius;doc.recompute()
errors={o.Name:abs(o.Shape.Volume-volumes[o.Name]) for o in objects}
assert all(e<1e-5 for e in errors.values())
assert all(o.Shape.isValid() for o in objects)
step=Part.Shape();step.read(str(ROOT/'cad/A_Page_at_Rest.step'))
roundtrip_error=abs(step.Volume-sum(volumes.values()))
assert step.isValid() and len(step.Solids)==3 and roundtrip_error<.01
report={'scope':'native parametric recomputation and CAD roundtrip, not physical safety',
        'fcstd_reopened_and_recomputed':True,
        'base_major_radius_plus_1mm_volume_increase_mm3':changed_base-volumes['Walnut_Base'],
        'left_stem_bottom_radius_plus_0_2mm_volume_increase_mm3':changed_support-volumes['Left_Brass_Cradle'],
        'restored_volume_errors_mm3':errors,'step_volume_roundtrip_error_mm3':roundtrip_error,
        'input_fcstd_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before,
        'no_cad_save_performed':True}
assert report['input_fcstd_unchanged']
(ROOT/'cad/parametric_recompute_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
