import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from soft_renderer import render_meshes
P=Path(__file__).resolve().parent; (P/'tmp').mkdir(exist_ok=True)

red = dict(vertices=[[-1,-1,1],[1,-1,-1],[0,1,0]],faces=[[0,1,2]],color=[1,0,0])
blue = dict(vertices=[[-1,-1,-1],[1,-1,1],[0,1,0]],faces=[[0,1,2]],color=[0,0,1])
kwargs=dict(width=300,height=300,camera=[0,0,5],target=[0,0,0],ortho_scale=3,supersample=1)
a=np.asarray(render_meshes([red,blue],**kwargs))
b=np.asarray(render_meshes([blue,red],**kwargs))
assert np.array_equal(a,b), 'Submission order changes non-coplanar occlusion'
assert a[200,110,0]>0 and a[200,110,2]==0
assert a[200,190,2]>0 and a[200,190,0]==0
reverse=dict(red,faces=[[2,1,0]])
assert np.array_equal(np.asarray(render_meshes([red],**kwargs)),np.asarray(render_meshes([reverse],**kwargs)))
assert render_meshes([],**kwargs).getpixel((0,0))==(244,241,232)
for bad in [dict(width=0),dict(supersample=1.5),dict(camera=[0,0,0]),dict(ortho_scale=0)]:
    try: render_meshes([red],**(kwargs|bad))
    except ValueError: pass
    else: raise AssertionError(bad)
for bad in [dict(faces=[[0,1,3]]),dict(color=[1.1,0,0]),dict(faces=[[0.,1.,2.]]),dict(vertices=[[float('nan'),0,0]])]:
    try: render_meshes([red|bad],**kwargs)
    except ValueError: pass
    else: raise AssertionError(bad)
render_meshes([red,blue],**kwargs).save(P/'tmp/renderer-test.png')
# Tilted cube intersected by a large triangle, with order-invariant depth.
v=np.array([[-.5,-.5,-.5],[.5,-.5,-.5],[.5,.5,-.5],[-.5,.5,-.5],[-.5,-.5,.5],[.5,-.5,.5],[.5,.5,.5],[-.5,.5,.5]])
f=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[3,2,6],[3,6,7],[0,3,7],[0,7,4],[1,5,6],[1,6,2]]
cube=dict(vertices=v,faces=f,color=[.8,.5,.15])
plane=dict(vertices=[[-1,-.8,0],[1,-.8,0],[0,1.3,0]],faces=[[0,1,2]],color=[.15,.4,.65])
k=kwargs|dict(camera=[3,2,5])
a=render_meshes([cube,plane],**k)
b=render_meshes([plane,cube],**k)
assert np.array_equal(np.asarray(a),np.asarray(b))
a.save(P/'tmp/renderer-test-cube.png')
# 960 triangles spread through the frame; realistic small-face workload.
meshes=[]
for i in range(80):
    vv=v*.1+np.array([(i%8-3.5)*.25,(i//8-4.5)*.25,0])
    meshes.append(dict(cube,vertices=vv))
t=time.perf_counter()
render_meshes(meshes,600,800,[3,2,5],[0,0,0],3,supersample=2)
print('All renderer checks passed; 960-triangle 600x800 SS2 render: %.3fs'%(time.perf_counter()-t))

# Z-up scene must match the previous top-down fallback view when remapped.
remapped=[]
for mesh in [red,blue]:
    v=np.asarray(mesh['vertices'])
    remapped.append(dict(mesh,vertices=np.column_stack((v[:,0],-v[:,2],v[:,1]))))
assert np.array_equal(np.asarray(render_meshes([red,blue],**kwargs)),np.asarray(render_meshes(remapped,**(kwargs|dict(camera=[0,-5,0])))))
print('World Z-up orientation and near-Z fallback passed')
