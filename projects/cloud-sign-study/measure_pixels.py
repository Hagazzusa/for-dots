"""Recompute the recorded post-hoc display RGB patches; writes a separate JSON."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
record=json.loads((R/'pixel_comparison.json').read_text())
images=[np.asarray(Image.open(R/p).convert('RGB'),dtype=np.float64) for p in ('draft.png','draft_corrected_sign.png')]
assert images[0].shape==images[1].shape==(400,600,3)
ys=[a@np.array([.2126,.7152,.0722]) for a in images]
out={'scope':record['scope'],'rois':{}}
for name,item in record['rois'].items():
 x0,y0,x1,y1=item['box'];assert 0<=x0<x1<=600 and 0<=y0<y1<=400
 out['rois'][name]={'box':item['box'],'mean_display_Y_before_after':[float(y[y0:y1,x0:x1].mean()) for y in ys]}
(R/'pixel_comparison_recomputed.json').write_text(json.dumps(out,indent=2)+'\n')
for name,item in out['rois'].items():
 assert np.allclose(item['mean_display_Y_before_after'],record['rois'][name]['mean_display_Y_before_after'],rtol=0,atol=1e-10)
print('Recorded post-hoc display means reproduced; no radiometric or significance claim.')
