"""Losslessly stitch the exact pixel interiors of overlapping scene renders."""
from pathlib import Path
from PIL import Image
import json
import numpy as np
P=Path(__file__).resolve().parent;W,H=1600,1200;out=Image.new('RGB',(W,H));coverage=0
for k in range(12):
 info=json.loads((P/'tmp'/f'region-{k:02d}.json').read_text());assert info['index']==k
 x0,y0,x1,y1=info['interior']
 # Blender stores normalized borders as float32 and truncates pixel coordinates.
 a,b,c,d=[int(np.float32(v/n)*n) for v,n in zip(info['padded'],[W,H,W,H])]
 im=Image.open(P/'tmp'/f'region-{k:02d}.png').convert('RGB');assert im.size==(c-a,d-b),(k,im.size,(c-a,d-b))
 crop=im.crop((x0-a,d-y1,x1-a,d-y0));assert crop.size==(x1-x0,y1-y0)
 out.paste(crop,(x0,H-y1));coverage+=(x1-x0)*(y1-y0)
assert coverage==W*H
out.save(P/'One-Body-Two-Shadows.png')
print('All 12 interior regions assembled without resizing; overlapping margins discarded.')
