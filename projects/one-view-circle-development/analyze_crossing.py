import numpy as np,json,math
from pathlib import Path
P=Path(__file__).resolve().parent
pts=[]
for k,t in enumerate([8,11.6,9.4,13,7.2,10.8,12.4,8.8]):
 for a in np.linspace(math.radians(k*45+3),math.radians(k*45+42),25):
  for r in [.81,1.25]:pts.append([r*np.cos(a)*t/10,-10+t,r*np.sin(a)*t/10])
pts=np.array(pts)
def proj(a):
 a=math.radians(a);right=np.array([np.cos(a),np.sin(a),0]);forward=np.array([-np.sin(a),np.cos(a),0]);depth=10+pts@forward
 return .5+48/36*np.column_stack((pts@right,pts[:,2]))/depth[:,None]
ref=proj(0)
def angle(t):
 u=(t-14)/10;u=u*u*(3-2*u);return 55-90*u
records=[]
for f in range(225,252):
 t=(f-1)/12;a=angle(t);delta=proj(a)-ref
 records.append({'frame':f,'seconds':round(t,4),'angle':round(a,5),'max_front_vertex_screen_delta':float(np.abs(delta).max()),'rms_front_vertex_screen_delta':float(np.sqrt(np.mean(delta**2)))})
summary={}
for threshold in [.005,.01,.02]:
 hits=[r for r in records if r['max_front_vertex_screen_delta']<=threshold]
 summary[str(threshold)]={'frames':[r['frame'] for r in hits],'duration_at_12fps':len(hits)/12}
(P/'crossing-analysis.json').write_text(json.dumps({'caution':'Coordinate difference from the initial view, not a measured human recognition threshold. Base-front vertices only.','windows':summary,'frames':records},indent=2)+'\n')
print(summary)
