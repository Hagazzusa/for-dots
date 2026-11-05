"""연결 하나를 제거한 인장 전용 평면 스프링 망의 정적 연구."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize
import subprocess
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/net'
N=9; DX=.15; DY=.12; K=180.; MASS=.04; G=9.81

def setup():
    points=np.array([[c*DX,r*DY] for r in range(N) for c in range(N)],dtype=float)
    edges=[]
    for r in range(N):
        for c in range(N):
            i=r*N+c
            if c<N-1: edges.append((i,i+1))
            if r<N-1: edges.append((i,i+N))
    edges=np.array(edges,dtype=int)
    lengths=np.linalg.norm(points[edges[:,1]]-points[edges[:,0]],axis=1)
    cut=np.flatnonzero(np.all(edges==[2*N+4,3*N+4],axis=1)).item()
    return points,edges,lengths,cut

def energy_gradient(flat, fixed, edges, rest):
    p=np.vstack((fixed,flat.reshape(-1,2)))
    d=p[edges[:,1]]-p[edges[:,0]]
    length=np.linalg.norm(d,axis=1)
    stretch=np.maximum(length-rest,0)
    energy=.5*K*np.dot(stretch,stretch)-MASS*G*np.sum(p[N:,1])
    grad=np.zeros_like(p);grad[N:,1]=-MASS*G
    force=K*stretch[:,None]*d/np.maximum(length[:,None],1e-15)
    np.add.at(grad,edges[:,0],-force);np.add.at(grad,edges[:,1],force)
    return float(energy),grad[N:].ravel()

def solve(initial,edges,rest):
    result=minimize(energy_gradient,initial[N:].ravel(),args=(initial[:N],edges,rest),jac=True,method='L-BFGS-B',options={'gtol':1e-9,'ftol':1e-15,'maxiter':10000,'maxls':50,'maxcor':30})
    p=np.vstack((initial[:N],result.x.reshape(-1,2)))
    residual=float(np.max(np.abs(result.jac)))
    if residual>2e-5: raise RuntimeError(f'residual {residual}: {result.message}')
    return p,{'optimizer_success':bool(result.success),'iterations':int(result.nit),'message':str(result.message),'max_free_force_component_N':residual,'energy_J':float(result.fun)}

def svg(points,edges):
    # 공통 투영. 사례마다 따로 확대·축소하지 않습니다.
    def xy(p):return 90+500*p[0],80+500*p[1]
    body=['<svg xmlns="http://www.w3.org/2000/svg" width="780" height="700" viewBox="0 0 780 700">','<rect width="780" height="700" fill="#f5f1e8"/>','<g stroke="#243a48" stroke-width="1.6" fill="none" stroke-linecap="round">']
    for a,b in edges:
        x1,y1=xy(points[a]);x2,y2=xy(points[b]);body.append(f'<path d="M{x1:.6f},{y1:.6f} L{x2:.6f},{y2:.6f}"/>')
    body.append('</g>')
    for p in points[:N]:
        x,y=xy(p);body.append(f'<circle cx="{x:.6f}" cy="{y:.6f}" r="3" fill="#a95740"/>')
    body.append('</svg>')
    return '\n'.join(body)+'\n'

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    initial,edges,rest,cut=setup()
    before,info_before=solve(initial,edges,rest)
    kept=np.delete(edges,cut,axis=0);newrest=np.delete(rest,cut)
    after,info_after=solve(before,kept,newrest)
    data={'model':'인장 전용 선형 스프링, 고정 상단 9점, 평면 정적 에너지 최소화','columns':N,'rows':N,'dx_m':DX,'dy_m':DY,'spring_N_per_m':K,'free_node_mass_kg':MASS,'gravity_m_per_s2':G,'cut_edge_index':cut,'cut_nodes':edges[cut].tolist(),'initial':initial.tolist(),'edges':edges.tolist(),'rest_lengths':rest.tolist(),'before':before.tolist(),'after':after.tolist(),'before_solve':info_before,'after_solve':info_after}
    (OUT/'model.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    for name,points,lines in [('before',before,edges),('erased',before,kept),('relaxed',after,kept)]:
        f=OUT/(name+'.svg');f.write_text(svg(points,lines))
        subprocess.run(['inkscape',str(f),'--export-type=png','--export-filename='+str(OUT/(name+'.png'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    print(json.dumps({'before':info_before,'after':info_after,'max_displacement_m':float(np.max(np.linalg.norm(after-before,axis=1)))},ensure_ascii=False))
