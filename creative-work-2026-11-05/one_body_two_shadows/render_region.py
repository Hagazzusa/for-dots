"""Render overlapping regions independently to bound final image-buffer memory."""
import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parent
k=int(sys.argv[sys.argv.index('--')+1]);W,H=1600,1200;cols,rows=4,3;pad=8
x=k%cols;y=k//cols
x0=x*400;y0=y*400;x1=min(W,x0+400);y1=min(H,y0+400)
a=max(0,x0-pad);b=max(0,y0-pad);c=min(W,x1+pad);d=min(H,y1+pad)
bpy.ops.wm.open_mainfile(filepath=str(P/'One-Body-Two-Shadows.blend'))
s=bpy.context.scene;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=a/W;s.render.border_max_x=c/W;s.render.border_min_y=b/H;s.render.border_max_y=d/H
s.render.filepath=str(P/'tmp'/f'region-{k:02d}.png')
bpy.ops.render.render(write_still=True)
(P/'tmp'/f'region-{k:02d}.json').write_text(json.dumps({'index':k,'full':[W,H],'interior':[x0,y0,x1,y1],'padded':[a,b,c,d]}))
