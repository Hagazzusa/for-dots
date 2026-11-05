"""Symbolic-normalized equilibrium examples, not component sizing.
W=1; P is an unspecified top follower preload normalized by W.
"""
import os,json,math
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/rain-clock-mpl')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
PTH=Path(__file__).resolve().parent
rows=[];residual_max=0.
for name,R in [('Outer',142.),('Inner',111.)]:
 h=1.5*R
 for f in [0,.25,.5,.75,1.]:
  for t in [0,.05,.1]:
   if f+t>1:continue
   d=14*f+21*t;Q=d/h
   # F uses coordinates X,Y,Z. Locations in nominal track plane.
   # radial lower contacts: n=(+/-sqrt(3)/2,0,-1/2)
   # top axial pushes rearward (+Y), lower axial pushes frontward (-Y).
   for preload in [0,.25,1.]: # mathematical unit tests, not selected preloads
    positions=[np.array([0.,0.,R]),np.array([math.sqrt(3)*R/2,0.,-R/2]),np.array([-math.sqrt(3)*R/2,0.,-R/2]),np.array([0.,-d,0.])]
    forces=[np.array([0.,Q,-preload]),np.array([-math.sqrt(3)*(1+preload)/2,-Q/2,(1+preload)/2]),np.array([math.sqrt(3)*(1+preload)/2,-Q/2,(1+preload)/2]),np.array([0.,0.,-1.])]
    F=sum(forces);M=sum(np.cross(r,v) for r,v in zip(positions,forces));residual_max=max(residual_max,float(max(abs(F).max(),abs(M).max())))
    assert np.allclose(F,0,atol=1e-12) and np.allclose(M,0,atol=1e-12)
   rows.append({'ring':name,'illustrative_axial_contact_radius_mm':R,'bead_weight_fraction_f':f,'tab_weight_fraction_t':t,'COM_front_offset_mm':d,'axial_contact_vertical_separation_mm':h,'top_axial_reaction_over_W':Q,'each_lower_opposite_axial_reaction_over_W':Q/2})
seating=[{'ring':name,'sidegap_mm':g,'illustrative_contact_radius_mm':R,'axial_center_seating_shift_mm':g/3,'rigid_plane_pitch_to_opposing_contacts_deg':math.degrees(math.atan(2*g/(1.5*R)))} for name,R in [('Outer',142.),('Inner',111.)] for g in [.2,.4,.6]]
result={'status':'Equilibrium of an idealized symmetric free-body only. Not load capacity, stability proof or friction-free mechanism.','coordinates':'X horizontal, Y rearward, Z upward. Track nominal plane Y=0. Weight acts at Y=-d.','formulas':{'COM':'d=14*f+21*t mm; remaining mass assumed in track plane; unknown actual distribution','radial':'N_left=N_right=1+P, top downward radial reaction=P; W=1; P unspecified >=0','axial':'top front support +Y: Q=d/h; each lower rear support -Y: Q/2; h=1.5*R_eff','pitch':'tan(|pitch|)=2*g/h for axially free-to-translate rigid plane seating top-front/lower-rear; actual broad contact geometry omitted'},'unit_test_max_force_or_moment_residual':residual_max,'illustrative_weight_fraction_cases':rows,'seating_examples':seating,'unresolved':['Actual COM and asymmetric bead/tab masses','Mechanism providing follower preload and return travel','Rolling versus sliding axial contacts and drag','Axle retention, stiffness, strength and material selection','Side-tab horizontal COM offset and in-plane gravity torque; radial contact-normal torque','Manual forces, tipping, pinch protection and dynamic response']}
(PTH/'load_path.json').write_text(json.dumps(result,indent=2));print(json.dumps({'residual':residual_max,'seating':seating},indent=2))
plt.rcParams.update({'figure.facecolor':'#111f28','axes.facecolor':'#111f28','text.color':'#e5eef3','font.family':'DejaVu Sans','font.size':12})
fig,ax=plt.subplots(figsize=(12,6));ax.set_xlim(-2,2);ax.set_ylim(-1.5,1.5);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('RAIN CLOCK / CLEARANCE IS NOT A LOAD PATH',x=.07,ha='left',y=.96,fontsize=21,fontweight='bold')
fig.text(.07,.88,'Ideal symmetric free-body · W = 1 · dimensions and masses are not component specifications',color='#abc0ce',fontsize=12)
a=np.linspace(0,2*np.pi,180);ax.plot(-.9+.65*np.cos(a),.65*np.sin(a),color='#c2a272',lw=3)
for x,z in [(-.9,.65),(-.9+.65*math.sqrt(3)/2,-.325),(-.9-.65*math.sqrt(3)/2,-.325)]:ax.plot(x,z,'o',color='#7caaa9',ms=10)
def arr(a,b,color='#7caaa9'):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':2.5,'color':color})
arr((-.9,1.03),(-.9,.7));ax.text(-1.25,1.12,'Top follower: P',fontsize=13)
arr((-.9+.9*math.sqrt(3)/2,-.45),(-.9+.52*math.sqrt(3)/2,-.26));arr((-.9-.9*math.sqrt(3)/2,-.45),(-.9-.52*math.sqrt(3)/2,-.26))
ax.text(-1.75,-.79,'Each lower radial reaction = 1 + P',fontsize=12)
arr((-.9,.15),(-.9,-.38),'#ecb16b');ax.text(-.83,-.13,'W = 1',color='#ecb16b')
ax.text(-1.5,-1.08,'Radial reactions balance weight.\nReturn force is unverified.',fontsize=11,color='#abc0ce')
# Side free-body schematic: front left, rear right.
ax.plot([.85,.85],[-.65,.65],color='#c2a272',lw=6);ax.plot([.45,.45],[.13,-.2],color='#ecb16b',lw=1,ls=':');arr((.45,.12),(.45,-.45),'#ecb16b');ax.text(.18,-.58,'W = 1',color='#ecb16b')
arr((.4,.65),(1.05,.65));arr((1.3,-.65),(.65,-.65));ax.text(.4,.83,'Top-front: Q toward rear',fontsize=12);ax.text(.65,-.88,'Lower-rear pair: −Q total',fontsize=12)
ax.annotate('',xy=(.85,.05),xytext=(.45,.05),arrowprops={'arrowstyle':'<->','color':'#abc0ce'});ax.text(.6,.13,'d',color='#abc0ce')
ax.text(1.16,.10,'Q × h = d\nQ = d / h',fontsize=15,color='#ecb16b');ax.text(.28,-1.15,'Axial contacts carry pitch.\nExtra gap permits extra tilt.',fontsize=11,color='#abc0ce')
fig.text(.07,.035,'No preload, force capacity, friction, bearing selection or safe hand operation has been established.',color='#edb291',fontsize=12)
fig.savefig(PTH/'load_path.png',dpi=140);fig.savefig(PTH/'load_path.svg');plt.close(fig)
