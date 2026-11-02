"""Bounded 2x spatial-resolution check of the narrowest measured penumbra.
Run after measure.py; does not alter its blend, profiles or full-matrix outputs.
"""
import bpy, json, hashlib
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent
protected=['measurements.json','edge_profiles.csv','Soft-Shadow-Measurement.blend']
before={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in protected}
base=json.loads((ROOT/'measurements.json').read_text()); old=base['cases'][0]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Soft-Shadow-Measurement.blend'))
s=bpy.context.scene; N=768; FIELD=4; s.render.resolution_x=s.render.resolution_y=N; s.render.threads_mode='FIXED'; s.render.threads=2; s.cycles.samples=96; s.cycles.use_denoising=False
filt=bpy.data.objects['Thin cyan filter']; filt.location.z=.5; bpy.data.objects['Finite square emitter'].data.size=.3
s.render.image_settings.file_format='OPEN_EXR'; s.render.image_settings.color_depth='32'
def render(name,hidden):
 filt.hide_render=hidden; s.render.filepath=str(ROOT/(name+'.exr')); bpy.ops.render.render(write_still=True); im=bpy.data.images.load(s.render.filepath,check_existing=False); assert im.is_float and im.colorspace_settings.name=='Linear Rec.709'; arr=np.array(im.pixels[:],dtype=np.float64).reshape(N,N,4); bpy.data.images.remove(im); return arr
control=render('convergence_768_control',True); result=render('convergence_768_filter',False)
# Twice the scanlines retains the original physical vertical averaging span.
profile=((result[N//2-16:N//2+16,:,0]/control[N//2-16:N//2+16,:,0]-.2)/.8).mean(axis=0)
x=(np.arange(N)+.5)*FIELD/N-FIELD/2
center=.6*4/3.5; full=.3*.5/3.5

def cross(threshold):
 ids=np.where((x>center-full/2-.06)&(x<center+full/2+.06))[0]
 for i in ids[:-1]:
  if profile[i]<=threshold and profile[i+1]>=threshold:
   return float(x[i]+(threshold-profile[i])/(profile[i+1]-profile[i])*(x[i+1]-x[i]))
 raise RuntimeError('Missing edge crossing')
x10=cross(.1); x90=cross(.9); width=x90-x10
np.savetxt(ROOT/'convergence_profile.csv',np.column_stack([x,profile]),delimiter=',',header='x_scene_units,normalized_unfiltered_fraction',comments='')
report={'scope':'One smallest-gap/smallest-emitter case with matching control, 2x spatial resolution only','resolution':N,'samples':s.cycles.samples,'seed':s.cycles.seed,'averaged_scanlines':32,'same_physical_scanline_span':True,'x10':x10,'x90':x90,'width_768':width,'width_384':old['measured_10_90_width'],'width_768_in_pixels':width/(FIELD/N),'relative_difference_384_vs_768':abs(old['measured_10_90_width']-width)/width,'uniform_source_approximation':old['uniform_emitter_10_90_approx'],'relative_difference_768_vs_ideal_approximation':abs(width-old['uniform_emitter_10_90_approx'])/old['uniform_emitter_10_90_approx'],'caveat':'A two-resolution comparison is not a formal converged limit or confidence interval; pixel filtering, sampling noise and angular emitter weighting remain.'}
after={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in protected}; assert before==after; report['original_matrix_preserved']=True
(ROOT/'convergence.json').write_text(json.dumps(report,indent=2)); print('CONVERGENCE',json.dumps(report))
