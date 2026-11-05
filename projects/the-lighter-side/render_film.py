"""Render a periodic mobile sequence; refuse to mix frames from different sources."""
from pathlib import Path
import argparse,hashlib,json,time,gc
from mobile import state,PERIOD,FPS,WIDTH,HEIGHT,CAMERA,TARGET,SCALE
from soft_renderer import render_meshes
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--study',action='store_true');ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int);args=ap.parse_args()
w,h,fps,ss=(400,400,12,2) if args.study else (WIDTH,HEIGHT,FPS,2)
out=P/'tmp'/('motion-study' if args.study else 'frames');out.mkdir(parents=True,exist_ok=True)
settings={'width':w,'height':h,'fps':fps,'duration':PERIOD,'frames':round(PERIOD*fps),'supersample':ss,'sources':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['mobile.py','soft_renderer.py']}}
record=out/'settings.json'
if record.exists():assert json.loads(record.read_text())==settings,'Sources/settings changed. Preserve existing frames in a new directory before rendering again.'
record.write_text(json.dumps(settings,indent=2)+'\n')
start=time.time()
for k in range(args.start,min(args.stop or settings['frames'],settings['frames'])):
 f=out/f'{k:04d}.png'
 if f.exists():continue
 meshes,_=state(k/fps);im=render_meshes(meshes,w,h,CAMERA,TARGET,SCALE,supersample=ss);im.save(f);im.close();gc.collect()
 if k%48==0:print(f'{k}/{settings["frames"]}, {time.time()-start:.1f}s',flush=True)
print(out,flush=True)
