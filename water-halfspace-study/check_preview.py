import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'LL.blend'));s=bpy.context.scene;cam=s.camera;proj=cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=400,y=300);inv=proj.inverted();rot=cam.matrix_world.to_3x3();arr=np.load(R/'renders/LL_linear.npy');Y=arr@np.array([.2126,.7152,.0722]);rois={'band_inside':[160,140,185,160],'band_outside':[165,202,185,222],'grid_bright':[143,238,173,258],'grid_dark':[212,238,242,258]};out={}
for name,(x0,y0,x1,y1) in rois.items():
 elevations=[];phases=[];positions=[]
 for y in range(y0,y1):
  for x in range(x0,x1):
   q=inv@Vector((2*(x+.5)/400-1,1-2*(y+.5)/300,-1,1));q/=q.w;d=(rot@Vector(q[:3])).normalized();top=cam.location+d*(-cam.location.z/d.z);trans=Vector((d.x/1.333,d.y/1.333,-math.sqrt(1-(d.x*d.x+d.y*d.y)/1.333**2)));floor=top+trans*(-.01/trans.z);elevations.append(math.degrees(math.asin(-d.z)));phases.append((math.floor(floor.x*5)+math.floor(floor.y*5)+math.floor(floor.z*5))%2);positions.append(list(floor))
 vals=Y[y0:y1,x0:x1];out[name]={'bounds_px':rois[name],'predicted_reflection_elevation_degrees':[min(elevations),max(elevations)],'predicted_checker_phase_counts':{str(k):phases.count(k) for k in (0,1)},'baseline_linear_luma_mean':float(vals.mean()),'baseline_linear_luma_std_spatial':float(vals.std())}
record={'fixed_before_other_matrix_cases':True,'basis':'LL actual preview only; all ROIs non-overlapping and frozen before HL/LH/HH renders.','model':'Snell transmitted ray intersects opaque checker floor 10 mm below single interface. Reflected elevation identifies environment band. Grid visibility supports passage through interface, not proof of a physically correct shallow volume.','display_choice':'Fixed exposure +2 for every PNG, selected after dark initial LL preview before other cases. EXRs remain scene-linear.','rois':out};(R/'records/roi_definition.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
