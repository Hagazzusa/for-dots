"""Plot finite sampled reachable components; not probabilities or proof."""
import os,json
from pathlib import Path
from collections import Counter
os.environ.setdefault('MPLCONFIGDIR','/tmp/rain-clock-mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent;d=json.loads((P/'results.json').read_text())
assert all(r['outcome'].startswith('inconclusive') for r in d['results']), 'Plot wording requires review for found paths'
plt.rcParams.update({'figure.facecolor':'#111f28','axes.facecolor':'#162a35','text.color':'#e5eef3','axes.labelcolor':'#d0e0e8','xtick.color':'#afc4d0','ytick.color':'#afc4d0','axes.edgecolor':'#4f6e80','font.family':'DejaVu Sans','font.size':11})
fig,axs=plt.subplots(1,2,figsize=(12,5.3));fig.subplots_adjust(left=.08,right=.87,top=.75,bottom=.23,wspace=.3)
fig.suptitle('RAIN CLOCK / A BOUNDED ESCAPE SEARCH',x=.08,ha='left',y=.96,fontsize=20,fontweight='bold')
fig.text(.08,.88,'Reachable sampled components (zoom) · no endpoint found is an INCONCLUSIVE result',fontsize=12,color='#e7b27a')
allposes=np.array([p for r in d['results'] for p in r['reachable_poses']]);xm=max(.2,max(abs(allposes[:,0]))+.05);ym=max(.2,max(abs(allposes[:,2]))+.05)
maxcount=max(max(Counter((round(p[0],6),round(p[2],6)) for p in r['reachable_poses']).values()) for r in d['results'])
for ax,r,title in zip(axs,d['results'],['A  Approximate translation following','B  Upper follower stuck outward']):
 c=Counter((round(p[0],6),round(p[2],6)) for p in r['reachable_poses']);pts=np.array(list(c));vals=list(c.values())
 sc=ax.scatter(pts[:,0],pts[:,1],c=vals,s=135,cmap='viridis',vmin=1,vmax=maxcount,edgecolors='#a8c4d0',linewidths=.4)
 ax.scatter([0],[0],marker='*',s=100,c='white',edgecolor='#111f28',linewidth=.6)
 ax.set(xlim=(-xm,xm),ylim=(-ym,ym),xlabel='Axial translation Y (mm)',ylabel='Pitch about X (degrees)');ax.grid(alpha=.2);ax.set_title(title,loc='left',fontsize=12,pad=14)
 ax.text(.03,.97,f"{r['reachable_grid_poses']} reachable / {r['unique_grid_poses_tested']} tested",transform=ax.transAxes,va='top',fontsize=10,color='#e6eef1')
cax=fig.add_axes([.9,.25,.02,.47]);cb=fig.colorbar(sc,cax=cax);cb.set_label('Number of reachable sampled lift levels');cb.ax.tick_params(colors='#afc4d0')
fig.text(.08,.105,'Domain: axial ±8 mm; lift −0.5…+2.5 mm; pitch ±6°. Other pose directions and forces excluded.',fontsize=10,color='#afc4d0')
fig.text(.08,.06,'Grid and midpoint BRep checks are not a continuous path proof. Star = initial adverse pose.',fontsize=10,color='#afc4d0')
fig.savefig(P/'reachable_components.png',dpi=140);fig.savefig(P/'reachable_components.svg');plt.close(fig)
summary={'conclusion':'Inconclusive: no extraction endpoint found in either explored sampled component. Not proof against escape.','results':[{k:v for k,v in r.items() if k not in ['reachable_poses','sampled_path','blocked_poses','uncertain_details']} for r in d['results']],'reachable_ranges':{r['mode']:{name:[float(min(p[i] for p in r['reachable_poses'])),float(max(p[i] for p in r['reachable_poses']))] for i,name in enumerate(['axial_Y_mm','lift_Z_mm','pitch_X_deg'])} for r in d['results']}}
(P/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
