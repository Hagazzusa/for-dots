"""영상 프레임만 생성한다. 인코더와 동시에 실행하지 않아 메모리를 줄인다."""
from pathlib import Path
import json,argparse
from build import P,irradiance,colorize,Image
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();a.directory.mkdir(parents=True,exist_ok=True)
m=json.loads((P/'model.json').read_text());fps=m['fps'];n=m['video_pixels_per_axis'];frames=round(fps*m['loop_seconds'])
for f in range(frames):
 I,_=irradiance(f/fps,m,m['video_rays_per_axis'],n)
 Image.fromarray(colorize(I)).save(a.directory/f'{f:04}.png')
 if f%48==0:print(f'{f}/{frames}',flush=True)
