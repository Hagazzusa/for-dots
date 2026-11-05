from pathlib import Path
import os, json
import numpy as np
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.plot-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=np.genfromtxt(ROOT/'edge_profiles.csv',delimiter=',',skip_header=1); high=np.genfromtxt(ROOT/'convergence_profile.csv',delimiter=',',skip_header=1); report=json.loads((ROOT/'convergence.json').read_text())
fig,ax=plt.subplots(figsize=(7.3,4.7),layout='constrained'); fig.patch.set_facecolor('#f5f2eb'); ax.set_facecolor('#f5f2eb')
ax.plot(base[:,0],base[:,1],'.-',color='#b09b77',label='384 px / 0.03658 width'); ax.plot(high[:,0],high[:,1],'.-',color='#26735e',label='768 px / 0.03470 width'); ax.axhline(.1,ls=':',color='#8c968c'); ax.axhline(.9,ls=':',color='#8c968c'); ax.set(xlim=(.64,.735),ylim=(-.04,1.04),xlabel='Receiver x coordinate (scene units)',ylabel='Normalized unfiltered fraction',title='The narrowest edge needs a precision caveat'); ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
fig.text(.5,-.015,'5.44% resolution difference; two resolutions do not establish a converged limit.',ha='center',fontsize=10)
fig.savefig(ROOT/'Resolution-Check.png',dpi=140,bbox_inches='tight')
