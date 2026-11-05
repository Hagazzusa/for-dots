"""Original balanced mobile geometry and prescribed periodic motion.

All geometry is generated here. Bars and plates carry modeled uniform mass;
suspension threads are ideal massless vertical lines. Motion is prescribed,
not a dynamic solution of wind, inertia, friction, or elastic deformation.
"""
from pathlib import Path
import numpy as np, math, json
P=Path(__file__).resolve().parent
PERIOD=16.;FPS=24;WIDTH,HEIGHT=800,800
CAMERA=(5.,-12.,6.5);TARGET=(.15,0.,2.85);SCALE=7.4
BAR_R=.012;THREAD_R=.004;THICK=.035;BAR_DENSITY=3.;PLATE_DENSITY=1.
DARK=(.23,.255,.25)

def rotation(a):
 c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def ellipse(rx,rz,n=48):
 return np.array([(rx*math.cos(2*math.pi*i/n),rz*math.sin(2*math.pi*i/n)) for i in range(n)])
def centered(poly):
 q=np.roll(poly,-1,axis=0);cross=poly[:,0]*q[:,1]-q[:,0]*poly[:,1];area=cross.sum()/2
 centroid=((poly+q)*cross[:,None]).sum(axis=0)/(6*area)
 return poly-centroid,area
profiles=[ellipse(.77,.59),ellipse(.30,.46),np.array([[-.35,-.26],[.35,-.26],[0,.58]]),ellipse(.24,.33)]
COLORS=[(.235,.39,.405),(.35,.48,.47),(.79,.335,.20),(.35,.48,.47)]
LEAVES=[]
for i,p in enumerate(profiles):
 p,area=centered(p);LEAVES.append({'name':'ABCD'[i],'profile':p,'mass':area*THICK*PLATE_DENSITY,'color':COLORS[i],'height':float(p[:,1].max())})

def branch(name,L,left,right):
 # The polygonal cylinder's volume, not the circumscribed circle's volume.
 area=12*.5*BAR_R**2*math.sin(2*math.pi/12);m=area*L*BAR_DENSITY
 p=(right*L+m*L/2)/(left+right+m)
 return {'name':name,'length':L,'left_arm':p,'right_arm':L-p,'rod_mass':m,'left_mass':left,'right_mass':right,'total_mass':left+right+m,'moment':-left*p+right*(L-p)+m*(L/2-p)}
LOW=branch('lower',1.42,LEAVES[2]['mass'],LEAVES[3]['mass'])
MID=branch('middle',2.15,LEAVES[1]['mass'],LOW['total_mass'])
TOP=branch('upper',2.6,LEAVES[0]['mass'],MID['total_mass'])
BRANCHES=[TOP,MID,LOW]

def cylinder(a,b,r,color,n=12):
 a,b=np.array(a,float),np.array(b,float);v=b-a;v/=np.linalg.norm(v);ref=np.array([0.,0.,1.]) if abs(v[2])<.9 else np.array([1.,0.,0.]);u=np.cross(v,ref);u/=np.linalg.norm(u);w=np.cross(v,u)
 ring=np.array([r*(math.cos(i*2*math.pi/n)*u+math.sin(i*2*math.pi/n)*w) for i in range(n)])
 verts=np.vstack([a+ring,b+ring,a,b]);faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([(i,j,n+j),(i,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)])
 return {'vertices':verts,'faces':faces,'color':color}

def plate(i,center,yaw):
 p=LEAVES[i]['profile'];n=len(p);vs=[]
 for y in [-THICK/2,THICK/2]:vs.extend([(x,y,z) for x,z in p])
 vs.extend([(0,-THICK/2,0),(0,THICK/2,0)]);fs=[]
 for k in range(n):
  j=(k+1)%n;fs.extend([(2*n,k,j),(2*n+1,n+j,n+k),(k,n+k,n+j),(k,n+j,j)])
 return {'vertices':np.array(vs)@rotation(yaw).T+center,'faces':fs,'color':LEAVES[i]['color']}

def state(t):
 u=2*math.pi*t/PERIOD
 angles=np.deg2rad([55-38*math.cos(u),75+32*math.sin(u+2.0),-82+42*math.sin(u-.85)])
 yaws=np.deg2rad([10+35*math.sin(u+.8),-15+55*math.sin(u+2.4),40+45*math.sin(u-.5),-35+55*math.sin(u+1.3)])
 meshes=[];centers=[];rods=[];threads=[]
 root=np.array([-.35,0.,4.8]);meshes.append(cylinder(root,root+[0,0,2.],THREAD_R,DARK,8))
 def addbar(b,origin,theta):
  R=rotation(theta);l=origin+R@np.array([-b['left_arm'],0,0]);r=origin+R@np.array([b['right_arm'],0,0]);meshes.append(cylinder(l,r,BAR_R,DARK));rods.append((l,r));return l,r
 a,j=addbar(TOP,root,angles[0]);mid=j+[0,0,-.8];meshes.append(cylinder(j,mid,THREAD_R,DARK,8));threads.append((j,mid))
 b,k=addbar(MID,mid,angles[0]+angles[1]);low=k+[0,0,-.8];meshes.append(cylinder(k,low,THREAD_R,DARK,8));threads.append((k,low))
 c,d=addbar(LOW,low,sum(angles))
 for i,(anchor,z,theta) in enumerate(zip([a,b,c,d],[1.55,2.65,2.,.95],[angles[0],sum(angles[:2]),sum(angles),sum(angles)])):
  center=np.array([anchor[0],anchor[1],z]);centers.append(center);top=center+[0,0,LEAVES[i]['height']];meshes.append(cylinder(anchor,top,THREAD_R,DARK,8));threads.append((anchor,top));meshes.append(plate(i,center,yaws[i]))
 return meshes,{'centers':np.array(centers),'bars':rods,'threads':threads,'angles':angles,'leaf_yaws':yaws}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--time',type=float,default=0);ap.add_argument('--output',default='tmp/probe.png');args=ap.parse_args()
 from soft_renderer import render_meshes
 meshes,_=state(args.time);im=render_meshes(meshes,WIDTH,HEIGHT,CAMERA,TARGET,SCALE,supersample=2);out=P/args.output;out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
 (P/'balance.json').write_text(json.dumps({'branches':BRANCHES,'plate_masses':{l['name']:l['mass'] for l in LEAVES},'limits':'Uniform mass geometry, massless threads, prescribed rotations; not a dynamic or fabrication simulation.'},indent=2)+'\n')
