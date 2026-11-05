"""Render bounded batches, validate all source frames, and encode the silent loop."""
from pathlib import Path
import subprocess,sys,json,shutil
from PIL import Image
from mobile import FPS,PERIOD,WIDTH,HEIGHT
P=Path(__file__).resolve().parent;count=round(FPS*PERIOD)
for k in range(0,count,12):
 subprocess.run([sys.executable,str(P/'render_film.py'),'--start',str(k),'--stop',str(min(k+12,count))],check=True)
for k in range(count):
 with Image.open(P/'tmp/frames'/f'{k:04d}.png') as im:
  assert im.size==(WIDTH,HEIGHT);im.verify()
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-framerate',str(FPS),'-i',str(P/'tmp/frames/%04d.png'),'-frames:v',str(count),'-c:v','libx264','-threads','1','-preset','veryfast','-x264-params','rc-lookahead=10:ref=1:bframes=2','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart','-an','-metadata','title=가벼운 쪽의 거리','-metadata','artist=닷돌이',str(P/'The-Lighter-Side.mp4')]
subprocess.run(cmd,check=True)
shutil.copyfile(P/'tmp/frames'/f'{8*FPS:04d}.png',P/'The-Lighter-Side.png')
print(P/'The-Lighter-Side.mp4')
