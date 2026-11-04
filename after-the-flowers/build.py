#!/usr/bin/env python3
"""Original orthographic still life; standard library + installed Inkscape."""
import math,json,subprocess,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
W,H=1600,1200; S=1080; CX,CY=760,610
# One orthonormal camera for every object. Units are nominal composition units, not product measurements.
R=(.8,.6,0); F=(-.6/math.sqrt(3.25),.8/math.sqrt(3.25),-1.5/math.sqrt(3.25)); U=(R[1]*F[2],-R[0]*F[2],R[0]*F[1]-R[1]*F[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def project(p):return CX+S*dot(p,R),CY-S*dot(p,U)
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
faces=[]
def face(points,color,name):
 a,b,c=points[:3];n=cross(tuple(b[i]-a[i] for i in range(3)),tuple(c[i]-a[i] for i in range(3)))
 if dot(n,F)<-1e-10:faces.append({'p':points,'color':color,'name':name,'depth':sum(dot(q,F) for q in points)/len(points)})
def poly2(points,color,name,z=.004):
 if points[0]==points[-1]:points=points[:-1]
 area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))
 if area<0:points=list(reversed(points))
 face([(x,y,z) for x,y in points],color,name)
def ring(cx,cy,r,z):return[(cx+r*math.cos(i*2*math.pi/72),cy+r*math.sin(i*2*math.pi/72),z) for i in range(72)]
def cylinder(cx,cy,r,z0,z1,top,side,name):
 a=ring(cx,cy,r,z0);b=ring(cx,cy,r,z1)
 face(b,top,name+'_top')
 for i in range(72):
  j=(i+1)%72
  angle=(i+.5)*2*math.pi/72
  # Flat facet tones are illustrative, not a lighting simulation.
  col=side[0] if math.cos(angle-2)>0 else side[1]
  face([a[i],a[j],b[j],b[i]],col,name+'_side')
# Two sheets, each supported by the table or the sheet below.
poly2([(-.335,-.245),(.185,-.245),(.185,.285),(-.335,.285)],'#b7b7a0','lower_paper',.002)
poly2([(-.315,-.225),(.215,-.225),(.215,.185),(.105,.295),(-.315,.295)],'#eadfbe','upper_paper',.004)
face([(.215,.185,.004),(.105,.295,.004),(.105,.185,.022)],'#f4ead0','folded_corner')
# A narrow old crease is a surface mark, not a raised strip.
poly2([(-.313,.05),(.213,.05),(.213,.052),(-.313,.052)],'#d8cba9','crease',.0042)
# One trimmed leafy stem remains on the paper; an invented small work trace.
poly2([(-.247,.151),(-.244,.153),(-.159,.035),(-.162,.033)],'#6c8260','stem',.0046)
poly2([(-.222,.119),(-.251,.126),(-.269,.151),(-.240,.148),(-.222,.119)],'#78916b','leaf_a',.0048)
poly2([(-.198,.085),(-.190,.123),(-.163,.139),(-.168,.109)],'#91a57a','leaf_b',.0048)
poly2([(-.162,.033),(-.159,.035),(-.157,.032),(-.160,.030)],'#c4b88b','stem_cut',.0049)
# Spool sits separately on the table, clear of paper edges.
cylinder(.36,.035,.076,0,.018,'#ccb387',('#ae936b','#bca378'),'lower_flange')
cylinder(.36,.035,.054,.018,.103,'#d6c398',('#b4a179','#c3af85'),'twine_core')
cylinder(.36,.035,.076,.103,.12,'#ddcaa1',('#bda37b','#c8b28a'),'upper_flange')
cylinder(.36,.035,.042,.1201,.1207,'#eee0ba',('#eee0ba','#eee0ba'),'label')
cylinder(.36,.035,.013,.1208,.121,'#627b73',('#627b73','#627b73'),'hole_mark')
# Loose string lies on the tabletop. It does not cross under the paper.
def bez(a,b,c,d,n=40):
 return [tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in range(3)) for t in [i/n for i in range(n+1)]]
cord=bez((.377,-.038,.001),(.48,-.16,.001),(.47,-.31,.001),(.28,-.34,.001))+bez((.28,-.34,.001),(.10,-.37,.001),(-.12,-.36,.001),(-.20,-.30,.001))[1:]
# Flat polygonal contact marks are separate from physical shadow claims.
shadow=ring(.371,.026,.085,0)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>꽃이 떠난 자리</title><desc>한 시점에서 비스듬히 내려다본 꽃집 작업대. 접힌 포장지와 작은 끈 실패만 남아 있는 독립 벡터 정물.</desc><path fill="#78938a" d="M0 0H1600V1200H0Z"/>']
def pstr(points):return ' '.join(f'{x:.5f},{y:.5f}' for x,y in map(project,points))
svg.append(f'<polygon points="{pstr(shadow)}" fill="#566f65" opacity=".32"/>')
svg.append(f'<polyline points="{pstr(cord)}" fill="none" stroke="#d9c69b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
ordered=[q for name in ['lower_paper','upper_paper','crease','folded_corner','stem','leaf_a','leaf_b','stem_cut'] for q in faces if q['name']==name]+sorted([q for q in faces if q['name'] not in ['lower_paper','upper_paper','crease','folded_corner','stem','leaf_a','leaf_b','stem_cut']],key=lambda q:q['depth'],reverse=True)
for q in ordered:svg.append(f'<polygon data-part="{q["name"]}" points="{pstr(q["p"])}" fill="{q["color"]}"/>')
svg.append('</svg>');(P/'after_the_flowers.svg').write_text('\n'.join(svg))
assert U[2]>0 and project((0,0,.1))[1]<project((0,0,0))[1]
assert abs(dot(R,F))<1e-10 and abs(dot(R,U))<1e-10 and abs(dot(F,U))<1e-10
assert all(abs(dot(v,v)-1)<1e-10 for v in [R,F,U])
# Object separation / vertical support checks.
paper_maxx=.215; spool_minx=.36-.076; gap=spool_minx-paper_maxx;assert gap>0
assert min(q['p'][i][2] for q in faces for i in range(len(q['p'])))>=0
assert all(not(-.335<x<.215 and -.245<y<.295) for x,y,z in cord)
report={'projection':'single orthographic camera','camera_right':R,'camera_up':U,'camera_forward':F,'screen_scale_px_per_unit':S,'paper_size_units':[.53,.52],'spool_diameter_height_units':[.152,.121],'paper_spool_x_clearance_units':gap,'checks':{'orthonormal_camera':True,'no_geometry_below_table':True,'spool_base_z_zero':True,'paper_spool_disjoint':True,'cord_does_not_cross_paper':True},'limits':['Artistic units, not production dimensions.','The fold is a rigid triangular approximation, not simulated paper.','Hole is a dark surface mark rather than a hollow model.','Contact tint is illustrative, not simulated light.']}
(P/'geometry_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['inkscape',str(P/'after_the_flowers.svg'),'--export-type=png',f'--export-filename={P/"after_the_flowers.png"}','--export-width=3200'],check=True,capture_output=True)
print(json.dumps(report))
