"""All-three-contact kinematics for two lower fixed guides + upper radial follower.
This is NOT equilibrium, force capacity, preload design or a guarantee of tracking.
"""
import os,json,math
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent
angles=np.array([0,2*np.pi/3,4*np.pi/3]);normals=np.column_stack((np.sin(angles),np.cos(angles)))
rows=[]
for name,r in [('Outer',139.),('Inner',108.)]:
 R=r+4;A=.25;N=4096;a=np.arange(N)*2*np.pi/N
 for deg in range(0,121,5):
  phase=math.radians(deg);rad=R+A*np.cos(3*(a-phase));v=np.column_stack((rad*np.sin(a),rad*np.cos(a)));seg=np.roll(v,-1,axis=0)-v;ss=(seg*seg).sum(axis=1)
  def state(q,details=False):
   c=q[:2];centers=(R+9)*normals;centers[0,1]+=q[2];gaps=[];contact_normals=[]
   for cc in centers:
    w=cc-c-v;t=np.clip((w*seg).sum(axis=1)/ss,0,1);d=w-t[:,None]*seg;j=np.argmin((d*d).sum(axis=1));distance=np.linalg.norm(d[j]);gaps.append(distance-9);contact_normals.append(d[j]/distance)
   if details:return centers,np.array(contact_normals)
   return gaps
  s=A*math.cos(3*phase);seed=[.0001,2*s,3*s];sol=least_squares(state,seed,bounds=([-1,-1,-1],[1,1,1]),ftol=1e-12,xtol=1e-12,gtol=1e-12,max_nfev=200)
  assert sol.success or max(abs(np.array(state(sol.x))))<1e-8, (name,deg,sol.x,state(sol.x),sol.message)
  residual=float(max(abs(np.array(state(sol.x)))));assert residual<1e-7, (name,deg,residual,sol.x,sol.message)
  c=sol.x[:2];centers,u=state(sol.x,True)
  pin_gap=float(min(np.linalg.norm(centers-c,axis=1)-(r+1)-11))
  # Radial force balance feasibility only: N(P)=N0+P*Np; no torque balance here.
  mat=np.column_stack((-u[1],-u[2]));N0=np.linalg.solve(mat,np.array([0,1]));Np=np.linalg.solve(mat,u[0])
  assert min(N0)>0 and min(Np)>0
  rows.append({'ring':name,'shape_phase_deg':deg,'shape_amplitude_mm':A,'center_x_mm':float(c[0]),'center_z_mm':float(c[1]),'upper_follower_radial_shift_mm':float(sol.x[2]),'max_contact_distance_residual_mm':residual,'upper_root_gap_at_outward_stop_mm':float(state([c[0],c[1],1.])[0]),'projected_lip_overlap_at_outward_stop_mm':float(2-state([c[0],c[1],1.])[0]),'conservative_circular_pin_envelope_to_lips_mm':pin_gap,'post_to_fixed_frame_mm':float(156.5-(r+13+sol.x[2]+3)) if name=='Outer' else None,'lower_normal_reactions_at_P0_over_W':N0.tolist(),'lower_normal_reaction_P_coefficients':Np.tolist()})
outer=[x for x in rows if x['ring']=='Outer'];inner=[x for x in rows if x['ring']=='Inner']
# Outer bead circular swept inner edge vs inner follower post; independent phases.
coupled=[]
for o in outer:
 for i in inner:
  center=np.array([o['center_x_mm'],o['center_z_mm']]);post=np.array([0.,121+i['upper_follower_radial_shift_mm']]);gap=128.5-np.linalg.norm(post-center)-3
  coupled.append(float(gap))
summary={name:{'follower_min_mm':min(x['upper_follower_radial_shift_mm'] for x in rows if x['ring']==name),'follower_max_mm':max(x['upper_follower_radial_shift_mm'] for x in rows if x['ring']==name),'sampled_extrema_only':True,'max_center_shift_mm':max(math.hypot(x['center_x_mm'],x['center_z_mm']) for x in rows if x['ring']==name),'min_pin_lip_gap_mm':min(x['conservative_circular_pin_envelope_to_lips_mm'] for x in rows if x['ring']==name)} for name in ['Outer','Inner']}
summary['minimum_sampled_projected_lip_overlap_failed_return_mm']=min(x['projected_lip_overlap_at_outward_stop_mm'] for x in rows)
summary['outer_min_post_frame_gap_mm']=min(x['post_to_fixed_frame_mm'] for x in outer);summary['min_outer_bead_to_inner_top_post_mm']=min(coupled);summary['max_contact_residual_mm']=max(x['max_contact_distance_residual_mm'] for x in rows)
result={'status':'Imposed contact geometry only. Follower must actually move to these positions; no return force or friction model supplied. No full moment equilibrium or 3D escape proof.','shape':'Only outer running surface has 0.25 mm third-harmonic error; bead/pin circle remains circular, moving with ring center.','support_layout':'Upper sliding guide at 90 degrees, lower fixed guides at 210 and 330 degrees, relative to +X.','numerics':'4096 polygon segments; 25 shape phases over 120-degree repeat per ring; local least-squares solve imposed all three root contacts.','provisional_geometric_follower_limits_mm':[-1.,1.],'summary':summary,'samples':rows}
(P/'contact_motion.json').write_text(json.dumps(result,indent=2));print(json.dumps(summary,indent=2))
