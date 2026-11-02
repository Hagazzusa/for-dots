"""Deterministic hypothetical geometry sensitivity; NOT manufacturing statistics.
First-order radial model plus independently optimized 4096-segment checks.
"""
import os,json,math,itertools
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/rain-clock-mpl')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy.optimize import minimize
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
rings={'Outer':{'R':143.,'motion_rad':.15},'Inner':{'R':112.,'motion_rad':.19}}
# R is the track OUTER contact radius, not centerline radius.
# y(theta)=offset + A sin(theta-phi) + R tan(tilt) cos(theta-psi).
# Unknown phases and independent roller errors: conservative envelope sums amplitudes.
axial=[]
for name,props in rings.items():
 for sidegap,offset,runout,tilt,alignment in itertools.product([.2,.4,.6],[0,.05,.1,.2],[0,.05,.1,.2],[0,.02,.05,.1,.2],[0,.05,.1,.25]):
  demand=abs(offset)+runout+props['R']*math.tan(math.radians(tilt))+alignment
  axial.append(dict(ring=name,sidegap_mm=sidegap,offset_mm=offset,axial_waviness_amplitude_mm=runout,tilt_deg=tilt,roller_axial_error_bound_mm=alignment,margin_mm=sidegap-demand))
thresholds={name:{str(g):math.degrees(math.atan(g/p['R'])) for g in [.2,.4,.6]} for name,p in rings.items()}
# Equal spacing means sum(n_i)=0. To first order the best minimum radial
# gap with free translation equals mean(e_i - shape_error_i). Recentring
# c=(2/3) sum((e_i-shape_error_i)n_i) equalizes the three gaps.
theta=np.arange(3)*2*np.pi/3; normals=np.column_stack((np.cos(theta),np.sin(theta)))
radial=[]
for name,p in rings.items():
 for profile,amp,phase,adjust in itertools.product(['eccentric_reference','oval_2','lobed_3','oversize'],[.05,.1,.25],np.arange(0,360,5),[0,.1,.25]):
  ph=math.radians(float(phase))
  if profile=='eccentric_reference':err=amp*np.cos(theta-ph)
  elif profile=='oval_2':err=amp*np.cos(2*(theta-ph))
  elif profile=='lobed_3':err=amp*np.cos(3*(theta-ph))
  else:err=np.full(3,amp)
  # Only roller 0 is moved radially outward; others remain unchanged.
  adjustment=np.array([adjust,0.,0.]);d=adjustment-err;c=2/3*(d[:,None]*normals).sum(axis=0);g=d-normals@c
  assert np.ptp(g)<1e-12
  radial.append(dict(ring=name,profile=profile,amplitude_mm=amp,phase_deg=int(phase),one_roller_outward_mm=adjust,first_order_best_min_gap_mm=float(g.mean()),center_translation_mm=float(np.linalg.norm(c))))
# Independent nonlinear 2D check. Circle guide rollers R9; polygon distance.
# Multiple starting points, translation restricted to +/- 1 mm. Not a global proof.
def exact(R,profile,A,phase,N=4096):
 a=np.arange(N)*2*np.pi/N;ph=math.radians(phase)
 if profile=='eccentric_reference':rad=np.full(N,R);shift=A*np.array([math.cos(ph),math.sin(ph)])
 else:
  rad=R+A*(np.cos((2 if profile=='oval_2' else 3)*(a-ph)) if profile!='oversize' else np.ones(N));shift=np.zeros(2)
 v=np.column_stack((rad*np.cos(a),rad*np.sin(a)))+shift; nxt=np.roll(v,-1,axis=0);seg=nxt-v;length=(seg*seg).sum(axis=1)
 centers=(R+9)*normals
 def gaps(c):
  out=[]
  for center in centers:
   q=center-c-v;t=np.clip((q*seg).sum(axis=1)/length,0,1);d=q-t[:,None]*seg;out.append(np.sqrt((d*d).sum(axis=1).min())-9)
  return np.array(out)
 runs=[]
 for x0 in [[0,0,-A],[-A,0,-A],[A,0,-A]]:
  r=minimize(lambda x:-x[2],x0,method='SLSQP',bounds=[(-1,1),(-1,1),(-2,2)],constraints=[{'type':'ineq','fun':lambda x:gaps(x[:2])-x[2]}],options={'ftol':1e-10,'maxiter':100})
  if r.success and min(gaps(r.x[:2])-r.x[2])>-1e-7:runs.append(r)
 assert runs,(R,profile,A,phase)
 r=max(runs,key=lambda r:r.x[2]);return {'ring_outer_radius_mm':R,'profile':profile,'amplitude_mm':A,'phase_deg':phase,'best_min_gap_mm':float(min(gaps(r.x[:2]))),'center_translation_mm':float(np.linalg.norm(r.x[:2])),'successful_starts':len(runs),'segments':N,'model':'local multi-start nonlinear polygon distance; not a global infeasibility certificate'}
nonlinear=[]
for name,p in rings.items():
 for profile,phase in [('eccentric_reference',0),('oval_2',0),('oval_2',15),('oval_2',30),('lobed_3',0),('lobed_3',30),('oversize',0)]:
  r=exact(p['R'],profile,.25,phase);r['ring']=name;nonlinear.append(r)
# Tighter segment count check of the two most informative outer-ring cases.
convergence=[exact(143,profile,.25,0,8192) for profile in ['oval_2','lobed_3']]
# Explicit hypothetical clearance budget; not simultaneous production tolerances.
coupled={'outer_beads_to_inner_rollers_axial':{'nominal_mm':6.4,'outer_bead_axial_excursion_mm':.5,'inner_roller_axial_reposition_mm':.5,'remaining_mm':5.4},'outer_beads_to_inner_posts_radial':{'nominal_mm':4.5,'outer_sweep_growth_mm':.5,'inner_post_outward_adjustment_mm':.5,'remaining_mm':3.5},'bead_pins_to_same_ring_roller_lips_radial':{'nominal_mm':1.,'moving_center_excursion_mm':.25,'roller_inward_error_mm':.25,'remaining_mm':.5},'moving_to_shelter_Y':{'nominal_mm':16.,'rearward_excursion_mm':.5,'remaining_mm':15.5}}
operating=[]
for name,p in rings.items():
 for initial in [0,30,60]:
  phases=math.radians(initial)+np.linspace(-p['motion_rad'],p['motion_rad'],193)
  gaps=-.25*np.cos(3*phases)
  operating.append({'ring':name,'initial_shape_phase_deg':initial,'motion_half_amplitude_deg':math.degrees(p['motion_rad']),'three_lobe_amplitude_mm':.25,'first_order_min_gap_mm':float(gaps.min()),'first_order_max_gap_mm':float(gaps.max())})
for row in convergence:
 match=next(x for x in nonlinear if x['ring']=='Outer' and x['profile']==row['profile'] and x['phase_deg']==0)
 assert abs(row['best_min_gap_mm']-match['best_min_gap_mm'])<.0001
assert thresholds['Outer']['0.2']<thresholds['Inner']['0.2']
result={'operating_motion_band_cases':operating,'warning' :'Hypothetical deterministic scenarios; no measured manufacturing distributions or recommended tolerances. Negative margin means overlap in this model, not measured friction or injury risk. Positive means only geometric room, not stable support.','axial_model':'Worst unknown phases envelope: sidegap - |offset| - axial waviness amplitude - R*tan(tilt) - roller alignment bound. Runout amplitude is half peak-to-peak for the sinusoid. R is outer track contact radius.','tilt_only_zero_margin_deg':thresholds,'axial_scenarios':axial,'radial_first_order_scenarios':radial,'nonlinear_spot_checks':nonlinear,'polygon_convergence_checks':convergence,'coupled_hypothetical_budgets':coupled}
(P/'results.json').write_text(json.dumps(result,indent=2))
# Scientific model plots, not a dashboard of observed manufacturing data.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.facecolor':'#162630','figure.facecolor':'#101e27','text.color':'#e7eff3','axes.labelcolor':'#d2dfe7','xtick.color':'#b8cbd7','ytick.color':'#b8cbd7','axes.edgecolor':'#5a7484','grid.color':'#34505f'})
fig,axs=plt.subplots(1,2,figsize=(13.5,5.2));fig.subplots_adjust(left=.07,right=.98,bottom=.23,top=.76,wspace=.26)
fig.suptitle('RAIN CLOCK / WHERE THE IDEAL GAPS DISAPPEAR',x=.07,y=.96,ha='left',fontsize=19,fontweight='bold')
fig.text(.07,.885,'Hypothetical geometry sensitivity · no fabricated parts or measured tolerances',color='#a8bdca',fontsize=12)
a=axs[0];tilts=np.linspace(0,.2,101)
for gap,color in [(.2,'#e8ae6a'),(.4,'#71bcb6'),(.6,'#9eafe8')]:a.plot(tilts,gap-.1-143*np.tan(np.radians(tilts)),label=f'{gap:.1f} mm side gap',color=color,lw=2.5)
a.axhline(0,color='#df7a6c',lw=1);a.fill_between(tilts,-.45,0,color='#813e3a',alpha=.15);a.set_ylim(-.45,.55);a.set_xlim(0,.2);a.set_title('A  Outer ring: axial clearance envelope',loc='left',pad=15);a.set_xlabel('Hypothetical track tilt (degrees)');a.set_ylabel('Remaining side gap (mm)');a.grid(alpha=.5);a.legend(frameon=False,labelcolor='#e7eff3',fontsize=10)
a.text(.02,-.40,'Below zero: geometric overlap',fontsize=10,color='#e6a097')
b=axs[1];ph=np.linspace(0,120,241)
b.plot(ph,np.zeros_like(ph),color='#71bcb6',lw=2.5,label='Round eccentric / oval: first order')
b.plot(ph,-.25*np.cos(np.radians(3*ph)),color='#e8ae6a',lw=2.5,label='3-lobe shape error, amplitude 0.25 mm')
b.axhline(0,color='#6e8796',lw=1);b.axhspan(-.3,0,color='#813e3a',alpha=.15);b.set_xlim(0,120);b.set_ylim(-.3,.3);b.set_title('B  Radial guides: allow the ring to recenter',loc='left',pad=15);b.set_xlabel('Shape phase relative to three rollers (degrees)');b.set_ylabel('Best minimum radial gap, first order (mm)');b.grid(alpha=.5);b.legend(frameon=False,labelcolor='#e7eff3',fontsize=9,loc='lower center')
fig.text(.07,.105,'A: 0.05 mm axial offset + 0.05 mm axial waviness reserved; roller alignment error set to zero.',fontsize=10,color='#b2c5d0')
fig.text(.07,.065,'B: fixed rollers at 120°; ring free to translate. Positive gap may mean lost contact—not good support.',fontsize=10,color='#b2c5d0')
fig.savefig(P/'sensitivity_plot.png',dpi=140);fig.savefig(P/'sensitivity_plot.svg');plt.close(fig)
summary={'axial_cases':len(axial),'radial_cases':len(radial),'nonlinear_checks':nonlinear,'tilt_only_zero_margin_deg':thresholds,'convergence':convergence}
(P/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
