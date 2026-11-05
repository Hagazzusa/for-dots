"""Repeatable sampled static geometry QA, not a dynamics/fabrication certification.

Uniform polygon-prism leaf masses, polygonal-cylinder rod masses, massless
threads. Segment clearances use circumscribed circular radii (conservative
relative to rendered polygonal rods/threads). Plate overlaps use convex SAT.
"""
from pathlib import Path
import argparse, json, math, hashlib
import numpy as np
from scipy.optimize import minimize_scalar
import mobile as m

P=Path(__file__).resolve().parent

def polygon_properties(p):
 q=np.roll(p,-1,axis=0); cr=p[:,0]*q[:,1]-q[:,0]*p[:,1]
 area=cr.sum()/2
 return abs(area), ((p+q)*cr[:,None]).sum(axis=0)/(6*area)

def point_prism_distance(p,poly):
 # Local prism is profile in x,z, extruded along y.
 q=p[[0,2]]; edges=np.roll(poly,-1,axis=0)-poly; w=q-poly
 cross=edges[:,0]*w[:,1]-edges[:,1]*w[:,0]
 inside=np.all(cross>=-1e-12) or np.all(cross<=1e-12)
 u=np.clip(np.sum(w*edges,axis=1)/np.sum(edges*edges,axis=1),0,1)
 d2=0. if inside else np.min(np.sum((w-u[:,None]*edges)**2,axis=1))
 return math.sqrt(d2+max(abs(p[1])-m.THICK/2,0.)**2)

def segment_prism_distance(a,b,center,yaw,poly):
 R=m.rotation(yaw); a=(a-center)@R; b=(b-center)@R
 f=lambda u: point_prism_distance(a+u*(b-a),poly)
 opt=minimize_scalar(f,bounds=(0.,1.),method='bounded',options={'xatol':1e-10})
 return min(f(0.),f(1.),opt.fun)

def prism_data(i,center,yaw):
 p=m.LEAVES[i]['profile']; R=m.rotation(yaw)
 vertices=np.array([(x,y,z) for y in [-m.THICK/2,m.THICK/2] for x,z in p])@R.T+center
 e=np.roll(p,-1,axis=0)-p
 edges=np.vstack([np.column_stack([e[:,0],np.zeros(len(e)),e[:,1]]),[0,1,0]])@R.T
 normals=np.vstack([np.column_stack([e[:,1],np.zeros(len(e)),-e[:,0]]),[0,1,0]])@R.T
 return vertices,edges,normals

def sat_gap(a,b):
 va,ea,na=a; vb,eb,nb=b
 axes=np.vstack([na,nb,np.cross(ea[:,None,:],eb[None,:,:]).reshape(-1,3)])
 norms=np.linalg.norm(axes,axis=1); axes=axes[norms>1e-10]/norms[norms>1e-10,None]
 pa=va@axes.T; pb=vb@axes.T
 return float(np.max(np.maximum(pa.min(axis=0)-pb.max(axis=0),pb.min(axis=0)-pa.max(axis=0))))

def aabb_gap(a,b):
 return float(np.linalg.norm(np.maximum(np.maximum(a.min(axis=0)-b.max(axis=0),b.min(axis=0)-a.max(axis=0)),0)))

def all_positions(t):
 meshes,_=m.state(t)
 return np.concatenate([x['vertices'] for x in meshes])

def check(samples):
 report={'source_sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(), 'model':'Uniform-mass static geometry with prescribed periodic poses, not a dynamic simulation.',
  'sampling':{'samples':samples,'period_seconds':m.PERIOD,'step_seconds':m.PERIOD/(samples-1),'continuous_time_collision_proof':False},
  'assumptions':['Vertical massless suspension threads; no wind, inertia, flexibility or friction.',
   'Collision checks exclude each leaf’s own attachment thread, but include all rods and all unrelated threads.',
   'Segment checks conservatively use circumscribed circular rod/thread radius; numerical minimization tolerance 1e-10.',
   'Plate-pair overlap uses convex separating-axis test; touch tolerance 1e-9.'], 'plates':{}}
 masses=[]
 for leaf in m.LEAVES:
  area,c=polygon_properties(leaf['profile']); mass=area*m.THICK*m.PLATE_DENSITY; masses.append(mass)
  report['plates'][leaf['name']]={'independent_mass':mass,'declared_mass_error':mass-leaf['mass'],'profile_centroid':c.tolist()}
 rod_masses=[12*.5*m.BAR_R**2*math.sin(2*math.pi/12)*b['length']*m.BAR_DENSITY for b in m.BRANCHES]
 torque_max=np.zeros(3); com_max=np.zeros(3); global_max=0.; global_z=[float('inf'),-float('inf')]
 minima={}; pair_minima={}; collisions={}; pair_tests=0; failures=[]
 for t in np.linspace(0,m.PERIOD,samples):
  meshes,s=m.state(float(t)); centers=s['centers']; rods=s['bars']; root=rods[0][0]+(rods[0][1]-rods[0][0])*m.TOP['left_arm']/m.TOP['length']
  origins=[root,s['threads'][0][1],s['threads'][1][1]]
  for j,(leaf_indices,rod_indices) in enumerate([(range(4),range(3)),(range(1,4),range(1,3)),(range(2,4),range(2,3))]):
   points=np.array([centers[i] for i in leaf_indices]+[(rods[i][0]+rods[i][1])/2 for i in rod_indices]); weights=np.array([masses[i] for i in leaf_indices]+[rod_masses[i] for i in rod_indices])
   com=np.average(points,axis=0,weights=weights); offset=com-origins[j]; moment=np.sum(np.cross(points-origins[j],np.column_stack([np.zeros(len(weights)),np.zeros(len(weights)),-9.81*weights])),axis=0)
   torque_max[j]=max(torque_max[j],np.linalg.norm(moment)); com_max[j]=max(com_max[j],np.linalg.norm(offset[:2]))
   if j==0:
    global_max=max(global_max,np.linalg.norm(offset[:2])); global_z=[min(global_z[0],com[2]),max(global_z[1],com[2])]
  # Recover each actual leaf yaw from its extrusion axis, independent of
  # whether the artistic motion uses inherited or absolute swivel angles.
  yaws=[]
  for i in range(4):
   verts=meshes[7+2*i]['vertices']; n=len(m.LEAVES[i]['profile'])
   extrusion=verts[n]-verts[0]
   yaws.append(math.atan2(-extrusion[0],extrusion[1]))
  prisms=[prism_data(i,centers[i],yaws[i]) for i in range(4)]
  segments=[('rod_'+str(i),a,b,m.BAR_R,None) for i,(a,b) in enumerate(rods)]+[('thread_'+str(i),a,b,m.THREAD_R,i-2 if i>=2 else None) for i,(a,b) in enumerate(s['threads'])]+[('root_thread',root,root+[0,0,2.],m.THREAD_R,None)]
  for i in range(4):
   for name,a,b,r,own in segments:
    if own==i: continue
    key=f'{m.LEAVES[i]["name"]}/{name}'; lower=aabb_gap(prisms[i][0],np.array([a,b]))-r
    if lower>0 and lower>minima.get(key,{'clearance':float('inf')})['clearance']: continue
    d=segment_prism_distance(a,b,centers[i],yaws[i],m.LEAVES[i]['profile'])-r
    if d<minima.get(key,{'clearance':float('inf')})['clearance']: minima[key]={'clearance':float(d),'time':float(t)}
    if d < -1e-9: collisions.setdefault(key,{'first_time':float(t),'sample_count':0})['sample_count']+=1
   for j in range(i+1,4):
    bound=aabb_gap(prisms[i][0],prisms[j][0]); pair_key=f'{m.LEAVES[i]["name"]}/{m.LEAVES[j]["name"]}'
    if bound<pair_minima.get(pair_key,{'clearance_lower_bound':float('inf')})['clearance_lower_bound']: pair_minima[pair_key]={'clearance_lower_bound':bound,'time':float(t)}
    if bound>1e-9: continue
    pair_tests+=1; gap=sat_gap(prisms[i],prisms[j]); key=f'{m.LEAVES[i]["name"]}/{m.LEAVES[j]["name"]}'
    if gap<=1e-9:
     hit=collisions.setdefault(key,{'first_time':float(t),'sample_count':0,'max_sat_penetration':0.}); hit['sample_count']+=1; hit['max_sat_penetration']=max(hit['max_sat_penetration'],-gap)
 h=1e-4; p0=all_positions(0.); p1=all_positions(m.PERIOD)
 v0=(all_positions(h)-all_positions(-h))/(2*h); v1=(all_positions(m.PERIOD+h)-all_positions(m.PERIOD-h))/(2*h)
 report['static_balance']={'units':'Arbitrary geometry/density model units; gravity scale 9.81. Not a physical material prediction.', 'branch_max_torque_model_units':dict(zip(['upper','middle','lower'],torque_max.tolist())),'branch_max_horizontal_COM_offset':dict(zip(['upper','middle','lower'],com_max.tolist())),'global_max_horizontal_COM_offset':global_max,'global_COM_z_range':global_z,'root_z':float(root[2])}
 report['loop']={'max_vertex_position_error':float(np.max(np.linalg.norm(p1-p0,axis=1))),'max_vertex_velocity_error':float(np.max(np.linalg.norm(v1-v0,axis=1))),'velocity_difference_step':h,'analytic_periodicity':'All pose angles are constants plus sines or cosines of 2*pi*t/PERIOD; position and all derivatives are periodic.'}
 report['collision_checks']={'plate_segment_minima':minima,'plate_pair_aabb_clearance_lower_bounds':pair_minima,'plate_pair_narrowphase_tests':pair_tests,'collisions':collisions,'note':'Collision-free samples do not prove collision freedom between samples. Only plates versus rods/threads and plates versus plates are tested; intended attachment contacts are excluded.'}
 if np.max(torque_max)>1e-9: failures.append('Nonzero static torque')
 if global_max>1e-9: failures.append('Global center of mass not below root')
 if report['loop']['max_vertex_position_error']>1e-8 or report['loop']['max_vertex_velocity_error']>1e-6: failures.append('Loop seam discontinuity')
 if collisions: failures.append('Sampled collision risks')
 report['failures']=failures; report['passed']=not failures
 return report

if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('--samples',type=int,default=1601); parser.add_argument('--output',default='geometry-qa.json'); args=parser.parse_args()
 if args.samples<2: parser.error('--samples must be >= 2')
 report=check(args.samples); (P/args.output).write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({k:report[k] for k in ['passed','failures','static_balance','loop']},indent=2)); print('Collisions:',report['collision_checks']['collisions'])
