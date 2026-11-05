"""Independent standard-library check of the delivered virtual profile data."""
import math,json
from pathlib import Path
p=Path(__file__).resolve().parent
v=json.loads((p/'profile_6pct.json').read_text());y=v['y'];h=v['height'];cap=v['cap']
assert len(y)==len(h)==841 and y[0]==-130 and y[-1]==500
assert all(math.isfinite(z) for z in y+h)
def cx(y):return 21*math.sin((y+25)/46)+.07*y
grade=[];conservative=[]
for i in range(len(y)-1):
 dy=y[i+1]-y[i];assert dy>0
 conservative.append(abs(h[i+1]-h[i])/dy)
 grade.append(abs(h[i+1]-h[i])/math.hypot(dy,cx(y[i+1])-cx(y[i])))
assert max(conservative)<=cap+1e-8
report={'sample_count':len(y),'finite':True,'strictly_increasing_y':True,'cap_fraction':cap,'maximum_conservative_y_grade_percent':100*max(conservative),'maximum_horizontal_chord_segment_grade_percent':100*max(grade),'passed':True,'scope':'Finite piecewise-linear virtual-profile check, not road safety certification.'}
(p/'profile_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
