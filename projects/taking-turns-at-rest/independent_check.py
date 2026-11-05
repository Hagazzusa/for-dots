"""이상화 모델의 별도 구현 검증. 실제 제작이나 안전을 검증하지 않는다.

독립 실험은 24초이며 영상은 parameters.json에 설정된 20초이다.
기본 실행은 표준 출력만 사용한다. --report 경로를 지정하면 JSON을 저장한다.
가져오기만 할 때는 적분, 매개변수 파일 읽기 및 파일 쓰기를 실행하지 않는다.
NumPy와 SciPy가 필요하다.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import find_peaks

L=.8; m=.14; g=9.81; a=.45; k=.9; d=.9
P=np.array([[-.45,0.],[.45,0.]])
I=m*L**2

def geometry(theta):
    return P+a*L*np.stack((np.sin(theta),-np.cos(theta)),axis=-1)

def force(theta):
    E=geometry(theta); r=E[1]-E[0]; ell=np.linalg.norm(r)
    f=k*(ell-d)*r/ell
    return np.array([f,-f])

def spring_torque(theta):
    tangent=a*L*np.stack((np.cos(theta),np.sin(theta)),axis=-1)
    return np.sum(force(theta)*tangent,axis=-1)

def rhs(t,y):
    th=y[:2]
    return np.r_[y[2:],(-m*g*L*np.sin(th)+spring_torque(th))/I]

def energy(y):
    th=y[:2]; v=y[2:]
    ell=np.linalg.norm(geometry(th)[1]-geometry(th)[0])
    return .5*I*np.sum(v*v)+m*g*L*np.sum(1-np.cos(th))+.5*k*(ell-d)**2

def spring_potential(theta):
    E=geometry(theta)
    return .5*k*(np.linalg.norm(E[1]-E[0])-d)**2

def validate_parameters():
    """고정된 검증 조건과 현재 작품의 물리값 및 초기조건을 비교한다."""
    path=Path(__file__).with_name('parameters.json')
    actual=json.loads(path.read_text())
    expected={
        'length_m':L, 'mass_kg':m, 'gravity_m_s2':g,
        'anchor_spacing_m':float(P[1,0]-P[0,0]), 'spring_fraction':a,
        'spring_k_n_m':k, 'spring_rest_m':d,
        'initial_angle_rad':[.24,0.],
        'initial_angular_velocity_rad_s':[0.,0.],
    }
    differences={key:{'expected':value,'actual':actual.get(key)}
                 for key,value in expected.items() if actual.get(key)!=value}
    if differences:
        raise ValueError('물리값 또는 초기조건이 변경되어 이전 검증을 재사용할 수 없습니다: '
                         +json.dumps(differences,ensure_ascii=False))
    return actual


def compare_separate_implementation(parameters):
    """별도 구현의 상태 순서를 맞추어 방정식과 영상 구간 궤적을 비교한다."""
    import importlib.util
    spec=importlib.util.spec_from_file_location('taking_turns_model',Path(__file__).with_name('model.py'))
    model=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    # 독립 구현: [θA, θB, ωA, ωB], 작품 구현: [θA, ωA, θB, ωB].
    mapping=np.array([0,2,1,3])
    samples=np.array([[.24,0.,0.,0.],[-.2,.3,.1,-.15],[.4,.4,-.2,.3],[.01,-.01,.02,-.03]])
    errors=[]
    for state in samples:
        other=np.asarray(model.rhs(0,state[mapping],parameters))[mapping]
        errors.append(float(np.max(np.abs(rhs(0,state)-other))))
    duration=parameters['duration_s']
    times=np.linspace(0,duration,int(round(duration*1000))+1)
    independent=solve_ivp(rhs,(0,duration),[.24,0.,0.,0.],method='DOP853',
                          rtol=2e-12,atol=2e-14,t_eval=times,max_step=.02)
    if not independent.success:
        raise RuntimeError(independent.message)
    other=model.integrate(parameters).sol(times)[mapping]
    difference=np.abs(independent.y-other)
    return {'duration_s':duration,
            'sample_rhs_max_abs_error':max(errors),
            'trajectory_angle_max_abs_error_rad':float(difference[:2].max()),
            'trajectory_speed_max_abs_error_rad_s':float(difference[2:].max())}


def run_checks():
    parameters=validate_parameters()
    T=np.linspace(0,24,24001)
    y0=np.array([.24,0,0,0])
    sol=solve_ivp(rhs,(0,24),y0,method='DOP853',rtol=2e-12,atol=2e-14,t_eval=T,max_step=.02)
    assert sol.success
    Y=sol.y
    energies=np.array([energy(y) for y in Y.T])
    w0=np.sqrt(g/L); w1=np.sqrt(g/L+2*k*a*a/m)
    # 각 진자의 단독 에너지와 진폭 대용값에서는 스프링 에너지를 제외한다.
    local=.5*I*Y[2:]**2+m*g*L*(1-np.cos(Y[:2]))
    proxy=np.sqrt(2*local/(m*g*L))
    # 진동 한 주기의 평균으로 빠른 진동에 따른 요동을 줄인다.
    window=int(round((2*np.pi/w0)/(T[1]-T[0])))
    from scipy.ndimage import uniform_filter1d
    mean_local=uniform_filter1d(local,size=window,axis=1,mode='nearest')
    interior=(T>2)&(T<13)
    i=np.flatnonzero(interior)[np.argmin(mean_local[0,interior])]
    j=np.flatnonzero(interior)[np.argmax(mean_local[1,interior])]
    returns=(T>14)&(T<23)
    r=np.flatnonzero(returns)[np.argmax(mean_local[0,returns])]
    peaks=[]
    for channel in range(2):
        idx,_=find_peaks(np.abs(Y[channel]),distance=1100)
        peaks.append([{'t_s':float(T[p]),'abs_angle_rad':float(abs(Y[channel,p]))} for p in idx])
    # 스프링 위치에너지를 별도로 유한차분하여 토크 부호를 확인한다.
    errors=[]
    for th in [np.array([.24,0.]),np.array([-.2,.3]),np.array([.4,.4]),np.array([.01,-.01])]:
        h=1e-6
        gradient=np.array([(spring_potential(th+np.eye(2)[q]*h)-spring_potential(th-np.eye(2)[q]*h))/(2*h) for q in range(2)])
        errors.append(float(np.max(np.abs(spring_torque(th)+gradient))))
    lengths=np.array([np.linalg.norm(geometry(y[:2])[1]-geometry(y[:2])[0]) for y in Y.T])
    result={
     'scope':'Ideal planar point-mass, massless rigid rods and massless bidirectional Hooke spring; no construction, physical accuracy, stability, or safety certification.',
     'equation_check':'Correct sign: r=E2-E1; F1=k*(ell-d)*r/ell and Q_i=F_i dot aL(cos(theta_i),sin(theta_i)). Q_spring=-gradient(V_spring).',
     'energy_expression':'E = 0.5*m*L^2*(theta_dot_1^2+theta_dot_2^2) + m*g*L*(2-cos(theta_1)-cos(theta_2)) + 0.5*k*(|E2-E1|-d)^2',
     'linearization':'theta_ddot_1=-(g/L)*theta_1+(k*a^2/m)*(theta_2-theta_1); second equation exchanges indices.',
     'linear_frequencies_rad_s':[float(w0),float(w1)],
     'linear_first_transfer_s':float(np.pi/(w1-w0)),
     'linear_first_return_s':float(2*np.pi/(w1-w0)),
     'numerical_first_low_left_smoothed_energy_s':float(T[i]),
     'numerical_first_high_right_smoothed_energy_s':float(T[j]),
     'numerical_first_return_smoothed_left_energy_s':float(T[r]),
     'near_transfer_left_fraction_of_total_energy':float(mean_local[0,i]/energies[0]),
     'near_transfer_right_fraction_of_total_energy':float(mean_local[1,i]/energies[0]),
     'initial_total_energy_J':float(energies[0]),
     'max_relative_energy_drift':float(np.max(abs(energies-energies[0]))/energies[0]),
     'finite_difference_spring_torque_max_error_Nm':max(errors),
     'spring_length_range_m':[float(lengths.min()),float(lengths.max())],
     'angle_abs_max_rad':[float(np.max(abs(Y[q]))) for q in range(2)],
     'angle_extrema':peaks,
     'interpretation':'24 s shows first transfer and first return, then the start of a second transfer. Timing from one-carrier-period averaged uncoupled pendulum energies is a descriptive visualization metric, not an exact full-energy partition. Complete instantaneous rest at transfer is not guaranteed.',
     'limitations':['The Hooke spring supports both extension and compression. A tension-only cord or real spring that buckles does not implement this model.','Both rods rotate freely about fixed independent pivots; no rigid link joins the bobs. The spring attaches at 45% of rod length.','Damping, rod/spring mass, finite bob size, out-of-plane motion, compliance, collisions and spring limits are absent.','Energy exchange is not literal transfer of amplitude as a conserved scalar. Energy includes a coupling term, and nonlinear motion is not an exactly sinusoidal beat.']
    }
    result["independent_experiment_duration_s"]=24
    result["video_duration_s"]=parameters["duration_s"]
    result["separate_implementation_comparison"]=compare_separate_implementation(parameters)
    return result


def main():
    parser=argparse.ArgumentParser(description='연결 진자의 이상화 모델을 별도 구현으로 확인합니다.')
    parser.add_argument('--report',type=Path,help='검증 JSON을 저장할 경로. 생략하면 파일을 쓰지 않습니다.')
    args=parser.parse_args()
    result=run_checks()
    output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.report is not None:
        args.report.write_text(output)
    print(output,end='')


if __name__=='__main__':
    main()
