"""Virtual profile study. Run with Python + numpy/scipy/matplotlib. No engineering claims."""
from pathlib import Path
import json,time,math,os,tempfile
os.environ.setdefault('MPLCONFIGDIR',tempfile.mkdtemp(prefix='quiet-road-mpl-'))
import numpy as np
from scipy.optimize import minimize,LinearConstraint
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
# Frozen natural terrain and planar centerline from quiet_road seed 1102.
def cx(y):return 21*np.sin((y+25)/46)+.07*y
def dx(y):return 21/46*np.cos((y+25)/46)+.07
def natural(x,y):
 base=3+.022*(y+80)+1.1*np.sin(y/58)
 hills=4*np.sin(x/75+y/110)+3*np.sin(y/90-.7)+3*np.cos(x/65-y/140)
 far=np.clip((y-210)/160,0,1);far=far*far*(3-2*far)
 return base+hills+far*(8+7*np.sin(x/110+y/180)+5*np.sin(x/65-y/120))
y=np.arange(-130,501,3.0);target=natural(cx(y),y);N=len(y)
D=np.diff(np.eye(N),axis=0);D2=np.diff(np.eye(N),n=2,axis=0)
LAMBDA=25.; H=np.eye(N)+LAMBDA*D2.T@D2
fine=np.arange(-130,500.001,.75);s=np.r_[0,np.cumsum(np.hypot(np.diff(cx(fine)),np.diff(fine)))];ny=natural(cx(fine),fine)
u=np.arange(-50,51)[None,:];yy=fine[:,None];xx=cx(yy)+u*np.sqrt(1+dx(yy)**2);nat=natural(xx,yy)
edge=np.where(u<0,3,3+4.5*np.exp(-((yy-22)/9)**4));blend=np.clip(np.maximum(0,np.abs(u)-edge-1.1)/40,0,1);blend=blend*blend*(3-2*blend)
def metrics(h):
 earth=(h[:,None]-nat)*(1-blend)
 return {'maximum_grade_percent':float(100*np.max(np.abs(np.diff(h)/np.diff(s)))),'maximum_cut_m':float(max(0,-earth.min())),'maximum_fill_m':float(max(0,earth.max())),'rms_centerline_displacement_m':float(np.sqrt(np.mean((h-ny)**2))),'maximum_centerline_displacement_m':float(np.max(np.abs(h-ny))),'rms_grade_change_per_m':float(np.sqrt(np.mean((np.diff(np.diff(h)/np.diff(s))/np.diff(s)[:-1])**2)))}
profiles={'Natural follow':ny};report={'scope':'Virtual aesthetic grade caps, not civil-road standards. Fixed planar centerline and original terrain.','grade_measure_definition':'Maximum finite-segment height difference divided by horizontal centerline chord length; not exact integrated arc length','solver':'SciPy SLSQP','scipy_version':scipy.__version__,'nodes':N,'knot_spacing_m_y':3,'lambda_second_difference':LAMBDA,'slope_smoothing':'Positive normalized Gaussian convolution, sigma 3 virtual m of y-distance; recentered to natural mean height','endpoint_constraints':'Free endpoint heights; not connected to external roads.','grade_constraint':'abs(delta height)<=cap*delta y; conservative versus true horizontal arc length. Piecewise-linear reconstruction preserves bound.','baseline':metrics(ny),'results':{}}
for cap in [.04,.06,.08]:
 start=time.perf_counter();result=minimize(lambda h:.5*(h-target)@(h-target)+.5*LAMBDA*np.sum((D2@h)**2),target,jac=lambda h:H@h-target,method='SLSQP',constraints=[LinearConstraint(D,-cap*np.diff(y),cap*np.diff(y))],options={'ftol':1e-9,'maxiter':300})
 elapsed=time.perf_counter()-start;h=np.interp(fine,y,result.x)
 # Positive normalized convolution of y-slopes preserves the cap while softening knot transitions.
 kernel=np.exp(-.5*(np.arange(-12,13)/4)**2);kernel/=kernel.sum()
 slopes=np.diff(h)/.75;slopes=np.convolve(np.pad(slopes,(12,12),mode='edge'),kernel,mode='valid')
 h=np.r_[0,np.cumsum(slopes*.75)];h+=np.mean(ny-h)
 label=f'{int(cap*100)}% cap';profiles[label]=h
 m=metrics(h);m.update({'solver_success':bool(result.success),'solver_message':str(result.message),'solver_iterations':int(result.nit),'solver_seconds':elapsed,'maximum_constraint_violation_m':float(max(0,np.max(np.abs(D@result.x)-cap*np.diff(y))))});report['results'][label]=m
 assert result.success and m['maximum_constraint_violation_m']<1e-6
 assert np.all(np.isfinite(h)) and m['maximum_grade_percent']<=100*cap+1e-6
 if cap==.06:(OUT/'profile_6pct.json').write_text(json.dumps({'y':fine.tolist(),'height':h.tolist(),'cap':cap,'interpolation':'linear','seed':1102},indent=2)+'\n')
(OUT/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(3,1,figsize=(10,9),sharex=True,layout='constrained');colors=['#777777','#9b6b98','#2a766d','#b68137']
for (name,h),color in zip(profiles.items(),colors):
 axs[0].plot(s,h,label=name,color=color,lw=1.8)
 axs[1].plot((s[1:]+s[:-1])/2,100*np.diff(h)/np.diff(s),color=color,lw=1.3)
 axs[2].plot(s,h-ny,color=color,lw=1.3)
axs[0].set(ylabel='Height (virtual m)',title='Gentler grades trade terrain fidelity for earthwork');axs[0].legend(ncol=4,frameon=False)
axs[1].set(ylabel='Signed grade (%)');axs[1].axhline(6,color='#2a766d',ls=':',lw=.8);axs[1].axhline(-6,color='#2a766d',ls=':',lw=.8)
axs[2].set(ylabel='Centerline fill / cut (m)',xlabel='Horizontal distance along fixed centerline (virtual m)');axs[2].axhline(0,color='#777777',lw=.7)
for ax in axs:ax.grid(alpha=.17)
fig.suptitle('Road into Evening · profile research\nDesign experiment only — not road-engineering compliance',fontsize=12)
fig.savefig(OUT/'profile_comparison.png',dpi=140);print(json.dumps(report,indent=2))
