#!/usr/bin/env python3
"""질량 없는 막대와 스프링으로 연결된 평면 점질량 진자 두 개."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parent

def parameters():return json.loads((ROOT/'parameters.json').read_text())
def geometry(theta,p):
 theta=np.asarray(theta)
 anchors=np.array([[-p['anchor_spacing_m']/2,0.],[p['anchor_spacing_m']/2,0.]])
 radial=np.column_stack((np.sin(theta),-np.cos(theta)))
 bobs=anchors+p['length_m']*radial
 links=anchors+p['length_m']*p['spring_fraction']*radial
 return anchors,bobs,links

def rhs(t,y,p):
 theta=np.asarray(y)[[0,2]];omega=np.asarray(y)[[1,3]]
 _,_,links=geometry(theta,p);delta=links[1]-links[0];length=np.linalg.norm(delta)
 force=p['spring_k_n_m']*(length-p['spring_rest_m'])*delta/length
 forces=np.array([force,-force]);a=p['spring_fraction']*p['length_m']
 tangent=a*np.column_stack((np.cos(theta),np.sin(theta)))
 torque=(forces*tangent).sum(axis=1)-p['mass_kg']*p['gravity_m_s2']*p['length_m']*np.sin(theta)
 acceleration=torque/(p['mass_kg']*p['length_m']**2)
 return [omega[0],acceleration[0],omega[1],acceleration[1]]

def energy(y,p):
 theta=np.asarray(y)[[0,2]];omega=np.asarray(y)[[1,3]]
 _,_,links=geometry(theta,p)
 kinetic=.5*p['mass_kg']*p['length_m']**2*np.dot(omega,omega)
 gravity=p['mass_kg']*p['gravity_m_s2']*p['length_m']*np.sum(1-np.cos(theta))
 spring=.5*p['spring_k_n_m']*(np.linalg.norm(links[1]-links[0])-p['spring_rest_m'])**2
 return kinetic+gravity+spring

def integrate(p=None):
 p=p or parameters();angles=p['initial_angle_rad'];speeds=p['initial_angular_velocity_rad_s'];y0=[angles[0],speeds[0],angles[1],speeds[1]]
 solution=solve_ivp(lambda t,y:rhs(t,y,p),[0,p['duration_s']],y0,method='DOP853',rtol=2e-12,atol=2e-14,dense_output=True,max_step=.025)
 assert solution.success
 return solution

if __name__=='__main__':
 p=parameters();s=integrate(p);times=np.arange(p['duration_s']*p['fps'])/p['fps'];values=s.sol(times).T
 np.savetxt(ROOT/'motion.csv',np.column_stack((times,values)),delimiter=',',header='time_s,theta_A_rad,omega_A_rad_s,theta_B_rad,omega_B_rad_s',comments='',fmt='%.12g')
 print('motion.csv',len(times),'frames')
