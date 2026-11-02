"""Read-only render checks; requires Pillow and numpy. Writes local QA evidence."""
from pathlib import Path
import json, subprocess
import numpy as np
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).resolve().parent
paths=sorted((root/'frames').glob('frame_*.png'))
assert len(paths)==48, f'Expected 48 frames; found {len(paths)}'
a=np.stack([np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)/255 for p in paths])
assert a.shape==(48,480,480,3)
assert np.isfinite(a).all()
changes=np.abs(a-np.roll(a,1,axis=0)).mean(axis=(1,2,3))
mean=a.mean(axis=(1,2,3))
report={'frame_count':len(paths),'shape':list(a.shape),'loop_seam_mean_absolute_rgb_change':float(changes[0]),'ordinary_adjacent_mean_absolute_rgb_change':float(changes[1:].mean()),'max_adjacent_mean_absolute_rgb_change':float(changes.max()),'brightness_min':float(mean.min()),'brightness_max':float(mean.max()),'no_empty_frame':bool((a.std(axis=(1,2,3))>.01).all()),'note':'Pixel differences include path-tracing noise; numerical transform closure is in validation_loop.json.'}
assert report['no_empty_frame']; assert changes[0] < 2*changes[1:].mean(), 'Unexpected seam discontinuity'
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate:format=duration','-of','json',str(root/'Garden-of-Light-loop.mp4')]))
report['video']=meta
assert meta['streams'][0]['nb_frames']=='48'; assert float(meta['format']['duration'])==4
(root/'render_qa.json').write_text(json.dumps(report,indent=2))
canvas=Image.new('RGB',(960,640),(240,237,230)); draw=ImageDraw.Draw(canvas)
for i,frame in enumerate([1,13,25,37,48,1]):
 im=Image.open(paths[frame-1]).convert('RGB').resize((320,320)); x=(i%3)*320; y=(i//3)*320; canvas.paste(im,(x,y)); draw.text((x+10,y+10),f'frame {frame:02d}',fill=(245,245,245))
canvas.save(root/'contact-sheet.jpg',quality=92)
print(json.dumps(report,indent=2))
