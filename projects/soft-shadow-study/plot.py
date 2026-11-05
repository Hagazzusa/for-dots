"""Static scientific evidence figure; values read directly from measurements."""
from pathlib import Path
import json
import numpy as np
import os
os.environ.setdefault("MPLCONFIGDIR",str(Path(__file__).resolve().parent/".plot-cache"))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent; report=json.loads((r/'measurements.json').read_text()); data=np.genfromtxt(r/'edge_profiles.csv',delimiter=',',names=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f5f2eb','axes.facecolor':'#f5f2eb','axes.edgecolor':'#60746d','text.color':'#283f38','axes.labelcolor':'#283f38'})
fig,(a,b)=plt.subplots(1,2,figsize=(10.6,4.5),layout='constrained'); colors=['#89aaa1','#4d8b7b','#1d5c50']; x=data[data.dtype.names[0]]
for i,gap in enumerate([.5,1,1.5]):
 row=report['cases'][i+3]; y=data[data.dtype.names[i+4]]; center=(row['x10']+row['x90'])/2
 a.plot(x-center,y,color=colors[i],label=f'Gap {gap:.1f}')
a.axhline(.1,color='#aaa99b',ls=':',lw=1); a.axhline(.9,color='#aaa99b',ls=':',lw=1); a.set(xlim=(-.4,.4),ylim=(-.04,1.04),xlabel='Distance from measured edge midpoint (scene units)',ylabel='Normalized unfiltered fraction',title='One broad emitter, three distances'); a.legend(frameon=False)
for width,color in [(.3,'#a28d68'),(.9,'#287660')]:
 rows=[v for v in report['cases'] if v['emitter_width']==width]; gaps=[v['filter_receiver_gap'] for v in rows]
 b.plot(gaps,[v['measured_10_90_width'] for v in rows],marker='o',color=color,label=f'Emitter width {width}')
 b.plot(gaps,[v['uniform_emitter_10_90_approx'] for v in rows],ls=':',color=color,alpha=.7,label='Uniform-source approximation' if width==.3 else None)
b.set(xlabel='Filter-to-receiver gap (scene units)',ylabel='10–90% edge width (scene units)',title='Greater separation softens the boundary',ylim=(0,None)); b.legend(frameon=False)
fig.suptitle('Soft edges without glass diffusion',fontsize=17); fig.savefig(r/'Penumbra-Evidence.png',dpi=140)
