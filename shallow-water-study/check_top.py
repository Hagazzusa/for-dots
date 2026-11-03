import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;E=R
results=[]
for path in [E/'baseline/dish.blend',R/'dish/Test.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(path));o=bpy.data.objects['Shallow water volume'];z=max(v.co.z for v in o.data.vertices);vs=sorted([tuple(v.co) for v in o.data.vertices if abs(v.co.z-z)<1e-8 and v.co.xy.length>.001],key=lambda p:math.atan2(p[1],p[0]));faces=[p for p in o.data.polygons if all(abs(o.data.vertices[i].co.z-z)<1e-8 for i in p.vertices)];results.append({'vertices':vs,'top_z':z,'top_faces':len(faces),'flat_top_faces':sum(not p.use_smooth for p in faces)})
a,b=results;assert len(a['vertices'])==len(b['vertices']);err=max(abs(x-y) for va,vb in zip(a['vertices'],b['vertices']) for x,y in zip(va,vb));out={'max_top_boundary_coordinate_difference_m':err,'top_boundary_unchanged_within_1e_8m':err<1e-8,'top_z_equal':a['top_z']==b['top_z'],'baseline_top_faces':a['top_faces'],'test_top_faces':b['top_faces'],'all_test_top_faces_flat':b['top_faces']==b['flat_top_faces']};(R/'dish/top_boundary_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
