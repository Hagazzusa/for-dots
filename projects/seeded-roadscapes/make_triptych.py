"""Scientific comparison layout; original render pixels remain unchanged."""
from pathlib import Path
import json,os,tempfile
os.environ.setdefault('MPLCONFIGDIR',tempfile.mkdtemp(prefix='roadscapes-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
p=Path(__file__).resolve().parent;r=json.loads((p/'seed_report.json').read_text());fig,axs=plt.subplots(1,3,figsize=(15,4.3),layout='constrained');fig.set_facecolor('#f6f2e9')
for ax,seed in zip(axs,r['selected_seeds']):
 rec=next(x for x in r['records'] if x['seed']==seed);ax.imshow(mpimg.imread(p/f'seed_{seed}.png'));ax.axis('off');ax.set_title(f"Seed {seed} · cut {rec['maximum_cut_depth_m']:.2f} m / fill {rec['maximum_fill_depth_m']:.2f} m",fontsize=10,pad=10)
fig.suptitle('Seeded Roadscapes · same road plan, camera and light\nTerrain phases, amplitudes and scales vary · 6% virtual aesthetic cap, not engineering standards',fontsize=12)
fig.savefig(p/'postcard_triptych.png',dpi=120,facecolor=fig.get_facecolor())
