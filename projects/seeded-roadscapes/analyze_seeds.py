"""12 bounded seeds; fixed planar road; virtual 6% y-grade fit. No engineering claims."""
from pathlib import Path
import json,hashlib,time
import numpy as np
from scipy.optimize import minimize,LinearConstraint
from landscape import parameters,SEEDS,cx,dx,natural,width
OUT=Path(__file__).resolve().parent
fine=np.arange(-130,500.001,.75);coarse=fine[::4];n=len(coarse);D=np.diff(np.eye(n),axis=0);D2=np.diff(np.eye(n),n=2,axis=0);H=np.eye(n)+25*D2.T@D2
cxx=np.array([cx(y) for y in fine]);dxx=np.array([dx(y) for y in fine]);arc=np.hypot(np.diff(cxx),np.diff(fine))
us=np.array(sorted(set([-220+i*2 for i in range(221)]+[-1200+i*20 for i in range(121)]+[-4.1,-3,0,3,4.1])))
terrain_y=np.r_[fine,[508+i*8 for i in range(115)]]
# Exact topology used by the renderer. Horizontal Jacobian is positive independently of heights.
meshx=np.array([cx(y) for y in terrain_y])[:,None]+us[None,:]*np.sqrt(1+np.array([dx(y) for y in terrain_y])[:,None]**2)
mesh_y=np.broadcast_to(terrain_y[:,None],meshx.shape)
# Both triangles of one diagonal triangulation per quad are checked, not just the centerline.
a=np.stack([meshx[:-1,1:]-meshx[:-1,:-1],mesh_y[:-1,1:]-mesh_y[:-1,:-1]],axis=-1)
b=np.stack([meshx[1:,1:]-meshx[:-1,:-1],mesh_y[1:,1:]-mesh_y[:-1,:-1]],axis=-1)
c=np.stack([meshx[1:,:-1]-meshx[:-1,:-1],mesh_y[1:,:-1]-mesh_y[:-1,:-1]],axis=-1)
normz1=a[...,0]*b[...,1]-a[...,1]*b[...,0];normz2=b[...,0]*c[...,1]-b[...,1]*c[...,0]
assert min(normz1.min(),normz2.min())>0
records=[];profiles={};fingerprints=[]
for seed in SEEDS:
 start=time.perf_counter();p=parameters(seed);assert p==parameters(seed)
 target=np.array([natural(cx(y),y,p) for y in coarse]);r=minimize(lambda h:.5*np.sum((h-target)**2)+12.5*np.sum((D2@h)**2),target,jac=lambda h:H@h-target,method='SLSQP',constraints=[LinearConstraint(D,-.06*np.diff(coarse),.06*np.diff(coarse))],options={'ftol':1e-9,'maxiter':300});assert r.success
 h=np.interp(fine,coarse,r.x);kernel=np.exp(-.5*(np.arange(-12,13)/4)**2);kernel/=kernel.sum();slope=np.convolve(np.pad(np.diff(h)/.75,(12,12),mode='edge'),kernel,mode='valid');h=np.r_[0,np.cumsum(slope*.75)];nh=np.array([natural(cx(y),y,p) for y in fine]);h+=np.mean(nh-h)
 assert np.max(np.abs(np.diff(h))/.75)<.060000001
 # Same signed earthwork depths as the prior study, excluding asphalt surface lift.
 earth=[]
 for y,hh in zip(fine,h):
  for u in range(-50,51):
   x=cx(y)+u*(1+dx(y)**2)**.5
   edge=3 if u<0 else width(y);blend=min(1,max(0,abs(u)-edge-1.1)/40);blend=blend*blend*(3-2*blend)
   earth.append((hh-natural(x,y,p))*(1-blend))
 vals=np.array([natural(x,y,p) for y in range(-100,501,30) for x in range(-150,151,30)])
 assert np.all(np.isfinite(vals)) and np.all(np.isfinite(h));fingerprints.append(vals)
 rec={'seed':seed,'parameters':p,'baseline_max_chord_grade_percent':float(100*np.max(np.abs(np.diff(nh))/arc)),'fitted_max_chord_grade_percent':float(100*np.max(np.abs(np.diff(h))/arc)),'max_conservative_y_grade_percent':float(100*np.max(np.abs(np.diff(h))/.75)),'maximum_cut_depth_m':float(max(0,-min(earth))),'maximum_fill_depth_m':float(max(0,max(earth))),'earthwork_samples':len(earth),'terrain_quads_tested':int(normz1.size),'terrain_triangles_tested':int(normz1.size*2),'non_upward_terrain_triangles':0,'minimum_triangle_vertical_cross_product':float(min(normz1.min(),normz2.min())),'road_faces_tested':840,'road_triangles_tested':1680,'non_upward_road_triangles':0,'solver_success':True,'solver_iterations':int(r.nit),'seconds':time.perf_counter()-start,'terrain_fingerprint_sha256':hashlib.sha256(vals.astype('<f8').tobytes()).hexdigest()}
 # Same fixed planar ribbon: explicit road triangle vertical normals.
 left=cxx-3*np.sqrt(1+dxx*dxx);right=cxx+np.array([width(y) for y in fine])*np.sqrt(1+dxx*dxx)
 assert np.all((right[:-1]-left[:-1])*np.diff(fine)>0) and np.all((right[1:]-left[1:])*np.diff(fine)>0)
 profiles[str(seed)]={'y':fine.tolist(),'height':h.tolist(),'parameters':p};records.append(rec)
# Deterministic max-min selection using the full terrain-height fingerprints, not props.
F=np.stack(fingerprints);dist=np.sqrt(np.mean((F[:,None,:]-F[None,:,:])**2,axis=2));i,j=np.unravel_index(np.argmax(dist),dist.shape);k=max((q for q in range(len(SEEDS)) if q not in (i,j)),key=lambda q:min(dist[q,i],dist[q,j]));selected=[SEEDS[q] for q in (i,j,k)]
report={'scope':'Original seeded terrain phase/amplitude/scale; fixed planar road. Virtual diagnostic, not road-engineering compliance.','topology_evaluation':'Shared fixed XY coordinates computed and checked once; positive orientation result applies to all 12 height fields, not 12 separate mesh builds','seed_count':len(SEEDS),'selected_seeds':selected,'selection':'Farthest terrain-height fingerprint pair then max-min third, 231 sample locations','cap_domain_y_m':[-130,500],'cap_percent':6,'seed_controls':'Terrain wave amplitudes, phases and scales; also deterministic decorative stones. Planar centerline unchanged.','parameter_bounds':{'amplitudes':[[3,7],[2,5],[2,4]],'phases_rad':[-3.141592653589793,3.141592653589793],'x_scales_m':[[70,110],[85,140]],'y_scales_m':[[100,160],[120,190],[150,220]]},'records':records}
(OUT/'seed_report.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'profiles.json').write_text(json.dumps(profiles)+'\n');print(json.dumps({'selected_seeds':selected,'results':[{k:r[k] for k in ['seed','baseline_max_chord_grade_percent','fitted_max_chord_grade_percent','maximum_cut_depth_m','maximum_fill_depth_m']} for r in records]},indent=2))
