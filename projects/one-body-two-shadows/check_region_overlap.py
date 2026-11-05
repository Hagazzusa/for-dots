from pathlib import Path
import numpy as np,json
from PIL import Image
P=Path(__file__).resolve().parent;regions=[]
for k in range(12):
 j=json.loads((P/'tmp'/f'region-{k:02d}.json').read_text());a,b,c,d=[int(np.float32(v/n)*n) for v,n in zip(j['padded'],[1600,1200,1600,1200])];im=np.asarray(Image.open(P/'tmp'/f'region-{k:02d}.png').convert('RGB'),dtype=np.int16);regions.append((a,b,c,d,im))
checks=[]
for i in range(12):
 for j in range(i+1,12):
  if not ((j==i+1 and i//4==j//4) or j==i+4):continue
  a,b,c,d,A=regions[i];e,f,g,h,B=regions[j];x0=max(a,e);y0=max(b,f);x1=min(c,g);y1=min(d,h);assert x1>x0 and y1>y0
  D=np.abs(A[d-y1:d-y0,x0-a:x1-a]-B[h-y1:h-y0,x0-e:x1-e]);mean=float(D.mean());q99=float(np.percentile(D,99));assert mean<2.5,(i,j,mean)
  checks.append({'pair':[i,j],'mean_absolute_rgb_difference_8bit':mean,'p99_absolute_rgb_difference_8bit':q99})
report={'comparisons':len(checks),'maximum_mean_absolute_difference':max(c['mean_absolute_rgb_difference_8bit'] for c in checks),'checks':checks,'scope':'Identical world-space pixel coordinates in overlapping independently rendered regions; residual differences are stochastic sampling and reconstruction near borders.'}
(P/'region-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
