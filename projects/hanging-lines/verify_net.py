"""망 연구의 별도 힘 합산·재계산. 기본 실행은 읽기 전용입니다."""
from pathlib import Path
import json, argparse
import numpy as np
from scipy.optimize import minimize
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent

def verify():
    d=json.loads((ROOT/'output/net/model.json').read_text())
    n=d['columns']; p=np.array(d['before']);q=np.array(d['after']);initial=np.array(d['initial'])
    edges=np.array(d['edges']);rest=np.array(d['rest_lengths']);cut=d['cut_edge_index']
    kept=np.delete(edges,cut,axis=0); lengths=np.delete(rest,cut)
    k=d['spring_N_per_m'];w=d['free_node_mass_kg']*d['gravity_m_per_s2']
    assert np.array_equal(p[:n],initial[:n]) and np.array_equal(q[:n],initial[:n])
    assert np.isfinite(p).all() and np.isfinite(q).all()
    assert edges.shape==(144,2) and kept.shape==(143,2)
    assert edges[cut].tolist()==d['cut_nodes']==[22,31]
    assert np.allclose(rest,np.linalg.norm(initial[edges[:,1]]-initial[edges[:,0]],axis=1),atol=1e-15,rtol=0)
    graph=[set() for _ in p]
    for a,b in kept: graph[a].add(b);graph[b].add(a)
    reached=set(range(n));front=list(reached)
    while front:
        for v in graph[front.pop()]:
            if v not in reached:reached.add(v);front.append(v)
    assert len(reached)==len(p)
    distance={int(v):0 for v in edges[cut]};front=list(distance)
    while front:
        u=front.pop(0)
        for v in graph[u]:
            if v not in distance:distance[v]=distance[u]+1;front.append(v)
    def evaluate(coords, links, natural):
        f=np.zeros_like(coords);f[n:,1]=w
        energy=-w*float(np.sum(coords[n:,1]))
        for (a,b),l0 in zip(links,natural):
            delta=coords[b]-coords[a];length=float(np.linalg.norm(delta))
            extension=max(length-l0,0.)
            energy+=.5*k*extension**2
            tension=k*extension*delta/max(length,1e-15)
            f[a]+=tension;f[b]-=tension
        return energy,f
    def solve_again(seed,links,natural):
        def objective(flat):
            coords=np.vstack((p[:n],flat.reshape(-1,2)))
            e,f=evaluate(coords,links,natural)
            return e,-f[n:].ravel()
        r=minimize(objective,seed[n:].ravel(),jac=True,method='L-BFGS-B',options={'gtol':1e-10,'ftol':1e-15,'maxiter':10000,'maxls':50,'maxcor':40})
        points=np.vstack((p[:n],r.x.reshape(-1,2)))
        assert np.max(np.abs(evaluate(points,links,natural)[1][n:]))<2e-5
        return points
    eb,fb=evaluate(p,edges,rest);eq,fq=evaluate(q,kept,lengths)
    er,fr=evaluate(p,kept,lengths)
    assert np.max(np.abs(fb[n:]))<2e-5 and np.max(np.abs(fq[n:]))<2e-5
    assert eq<er
    analytic=initial.copy()
    for row in range(1,n):
        analytic[row*n:(row+1)*n,1] += sum((n-j)*w/k for j in range(1,row+1))
    analytic_error=float(np.max(np.abs(analytic-p)))
    assert analytic_error<1e-8
    slack=lengths-np.linalg.norm(q[kept[:,1]]-q[kept[:,0]],axis=1)
    slack_edges=[kept[i].tolist() for i in np.flatnonzero(slack>1e-6)]
    displacement=np.linalg.norm(q-p,axis=1)
    far=[i for i in range(n,len(p)) if distance[i]>=2]
    assert max(displacement[far])>.01
    support=np.sum(fq[:n],axis=0)
    assert np.linalg.norm(support-[0,w*(len(p)-n)])<.0001
    seed=q.copy();seed[n:]+=1e-4*np.sin(np.arange((len(p)-n)*2)).reshape(-1,2)
    repeat=solve_again(seed,kept,lengths)
    repeat_error=float(np.max(np.linalg.norm(repeat-q,axis=1)))
    assert repeat_error<1e-5
    low=int(np.flatnonzero(np.all(edges==[22,23],axis=1))[0])
    low_points=solve_again(p,np.delete(edges,low,axis=0),np.delete(rest,low))
    low_error=float(np.max(np.linalg.norm(low_points-p,axis=1)))
    assert low_error<1e-6
    for name,points,links in [('before',p,edges),('erased',p,kept),('relaxed',q,kept)]:
        tree=ET.parse(ROOT/f'output/net/{name}.svg');ns={'s':'http://www.w3.org/2000/svg'}
        paths=tree.findall('.//s:path',ns);assert len(paths)==len(links)
        for path,(a,b) in zip(paths,links):
            expected=f'M{90+500*points[a,0]:.6f},{80+500*points[a,1]:.6f} L{90+500*points[b,0]:.6f},{80+500*points[b,1]:.6f}'
            assert path.attrib['d']==expected
        projected=points*[500,500]+[90,80]
        assert np.all(projected>[3,3]) and np.all(projected<[777,697])
        with Image.open(ROOT/f'output/net/{name}.png') as im:im.load();assert im.size==(780,700)
    return {'절단 전 해석식 최대 좌표 차이 m':analytic_error,'자연길이보다 1마이크로미터 이상 짧은 연결':slack_edges,'최대 단축 m':float(max(slack)),'고정점과 연결성':True,'삭제 연결 노드':edges[cut].tolist(),'원래 연결 수':len(edges),'삭제 뒤 연결 수':len(kept),'절단 전 최대 잔류 힘 성분 N':float(np.max(np.abs(fb[n:]))),'절단 뒤 최대 잔류 힘 성분 N':float(np.max(np.abs(fq[n:]))),'절단 뒤 잔류 힘 성분 RMS N':float(np.sqrt(np.mean(fq[n:]**2))),'한 점 중량 N':w,'삭제 연결의 원래 인장력 N':float(k*max(np.linalg.norm(p[edges[cut,1]]-p[edges[cut,0]])-rest[cut],0)),'같은 삭제 후 에너지 함수로 평가한 재평형 감소 J':float(er-eq),'최대 이동 m':float(max(displacement)),'자유점 RMS 이동 m':float(np.sqrt(np.mean(displacement[n:]**2))),'절단 두 끝에서 그래프 거리 2 이상 최대 이동 m':float(max(displacement[far])),'작은 초기 교란 재계산 최대 좌표 차이 m':repeat_error,'저인장 가로 연결 삭제 최대 이동 m':low_error,'저인장 대조 삭제 노드':edges[low].tolist(),'SVG 전 좌표 및 PNG 디코드 검사':True,'한계':'정적 인장 전용 평면 스프링 모델의 두 절단 사례입니다. 전역 유일성·동역학·충돌·재료 물성·실물 제작은 검증하지 않았습니다.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report');args=parser.parse_args()
    result=json.dumps(verify(),ensure_ascii=False,indent=2)+'\n'
    if args.report:Path(args.report).write_text(result)
    print(result,end='')
