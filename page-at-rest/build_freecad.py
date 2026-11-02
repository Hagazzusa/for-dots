"""Build native parametric FreeCAD shapes and export their exact tessellations.

Run with system Python 3.13 and PYTHONPATH=/usr/lib/freecad-python3/lib.
The FCStd uses only native Ellipse, Extrusion, Fillet, Circle, Loft and MultiFuse
features; no pickle proxy, external macro or absolute file link is required.
"""
from pathlib import Path
import json, math, hashlib, sys
import FreeCAD as App
import Part, MeshPart
from geometry import page_point, cradle_point

ROOT=Path(__file__).resolve().parent
PARAMS=json.loads((ROOT/'parameters.json').read_text())
OUT=ROOT/'cad'; OUT.mkdir(exist_ok=True)
D=App.newDocument('A_Page_at_Rest')

def circle(name, center, radius, normal=(0,0,1)):
    obj=D.addObject('Part::Circle',name)
    obj.Radius=radius
    obj.Placement=App.Placement(App.Vector(*center),App.Rotation(App.Vector(0,0,1),App.Vector(*normal)))
    obj.Visibility=False
    return obj

def loft(name, stations):
    sections=[circle(name+'_Section_%02d'%i,*s) for i,s in enumerate(stations)]
    obj=D.addObject('Part::Loft',name); obj.Sections=sections; obj.Solid=True; obj.Ruled=False
    obj.MaxDegree=3
    D.recompute()
    return obj

b=PARAMS['base']
ellipse=D.addObject('Part::Ellipse','Base_Ellipse')
ellipse.MajorRadius=b['major_radius']; ellipse.MinorRadius=b['minor_radius']; ellipse.Visibility=False
extr=D.addObject('Part::Extrusion','Base_Extrusion'); extr.Base=ellipse
extr.Dir=App.Vector(0,0,b['height']); extr.Solid=True; extr.Visibility=False
D.recompute()
base=D.addObject('Part::Fillet','Walnut_Base'); base.Base=extr
base.Edges=[(i+1,b['edge_radius'],b['edge_radius']) for i,e in enumerate(extr.Shape.Edges) if e.Length>100]
D.recompute()
assert base.Shape.isValid() and len(base.Shape.Solids)==1
final=[base]
seat_samples=[]

for page in PARAMS['pages']:
    side=page['side']; tag='Left' if side<0 else 'Right'
    a=PARAMS['supports']['cradle_start']; z=PARAMS['supports']['cradle_end']
    us=[a+(z-a)*i/12 for i in range(13)]
    stations=[]
    for u in us:
        p=cradle_point(page,PARAMS,u)
        p0=cradle_point(page,PARAMS,u-0.0001); p1=cradle_point(page,PARAMS,u+0.0001)
        tangent=tuple(p1[k]-p0[k] for k in range(3))
        stations.append((p,PARAMS['supports']['radius'],tangent))
        edge=page_point(page,PARAMS['paper'],u,0)
        seat_samples.append({'page':page['name'],'u':u,'edge_mm':edge,'cradle_center_mm':p,
                             'intentional_insertion_mm':PARAMS['supports']['seat_insertion']})
    rail=loft(tag+'_Cradle_Loft',stations); rail.Visibility=False
    join=cradle_point(page,PARAMS,0.62)
    foot=(side*44,join[1]-7,b['height']-PARAMS['supports']['base_insertion'])
    stem_stations=[]
    for i in range(7):
        t=i/6
        p=(foot[0]*(1-t)+join[0]*t-side*2.4*math.sin(math.pi*t),
           foot[1]*(1-t)+join[1]*t,
           foot[2]*(1-t)+join[2]*t)
        r=2.6*(1-t)+1.65*t
        stem_stations.append((p,r,(0,0,1)))
    stem=loft(tag+'_Stem_Loft',stem_stations); stem.Visibility=False
    support=D.addObject('Part::MultiFuse',tag+'_Brass_Cradle')
    support.Shapes=[rail,stem]; support.Refine=True; D.recompute()
    final.append(support)

D.recompute()
report={'scope':'virtual geometric validation only; not manufacturing, structural, electrical or thermal safety',
        'freecad_version':App.Version()[:3], 'unit':'mm','objects':[],
        'seat_samples':seat_samples,'intended_base_insertion_mm':PARAMS['supports']['base_insertion']}
mesh_payload={'schema':1,'source':'native FreeCAD shapes','coordinate_unit':'mm','up_axis':'Z',
              'parameter_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),'parts':[]}
for obj in final:
    sh=obj.Shape
    assert sh.isValid() and len(sh.Solids)==1 and sh.Volume>0,(obj.Name,'invalid solid')
    sh.check(True)
    mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=0.06,AngularDeflection=0.10,Relative=False)
    vertices,faces=mesh.Topology
    vs=[[float(v.x),float(v.y),float(v.z)] for v in vertices]; fs=[list(f) for f in faces]
    assert all(math.isfinite(x) for v in vs for x in v)
    bounds=[sh.BoundBox.XMin,sh.BoundBox.YMin,sh.BoundBox.ZMin,sh.BoundBox.XMax,sh.BoundBox.YMax,sh.BoundBox.ZMax]
    mesh_payload['parts'].append({'name':obj.Name,'material':'walnut' if obj==base else 'brass',
                                 'vertices':vs,'faces':fs,'shape_bounds_mm':bounds,'volume_mm3':sh.Volume})
    report['objects'].append({'name':obj.Name,'valid':sh.isValid(),'solids':len(sh.Solids),
                              'volume_mm3':sh.Volume,'vertices':len(vs),'triangles':len(fs)})
    obj.Visibility=True
report['support_pair_intersection_mm3']=final[1].Shape.common(final[2].Shape).Volume
assert report['support_pair_intersection_mm3']<1e-8
report['support_base_intended_seats_mm3']=[o.Shape.common(base.Shape).Volume for o in final[1:]]
assert all(0<v<30 for v in report['support_base_intended_seats_mm3'])
mesh_path=OUT/'parts_mesh.json'; mesh_path.write_text(json.dumps(mesh_payload,separators=(',',':'))+'\n')
cad_path=OUT/'A_Page_at_Rest.FCStd'; D.recompute(); D.saveAs(str(cad_path))
step_path=OUT/'A_Page_at_Rest.step'; Part.export(final,str(step_path))
names=[o.Name for o in final]
App.closeDocument(D.Name)
reopened=App.openDocument(str(cad_path))
report['fcstd_reopened_valid']=all(reopened.getObject(n).Shape.isValid() and len(reopened.getObject(n).Shape.Solids)==1 for n in names)
assert report['fcstd_reopened_valid']
report['native_parametric_objects']=len(reopened.Objects)
step=Part.Shape(); step.read(str(step_path)); report['step_reopened_valid']=step.isValid()
report['step_solid_count']=len(step.Solids)
assert report['step_reopened_valid'] and report['step_solid_count']==3
report['mesh_sha256']=hashlib.sha256(mesh_path.read_bytes()).hexdigest()
(OUT/'geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='seat_samples'},indent=2))
