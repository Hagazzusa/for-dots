#!/usr/bin/env python3
"""작은 프레임 묶음으로 렌더해 무음 영상을 만든다. 별도 사본에서 실행한다."""
from pathlib import Path
import subprocess,sys
from model import ROOT,parameters

def main():
 p=parameters();subprocess.run([sys.executable,str(ROOT/'model.py')],check=True)
 n=p['duration_s']*p['fps']
 for start in range(0,n,12):subprocess.run([sys.executable,str(ROOT/'render.py'),'--start',str(start),'--stop',str(min(n,start+12))],check=True,stdout=subprocess.DEVNULL)
 out=ROOT/'Taking-Turns-at-Rest.mp4'
 subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-framerate',str(p['fps']),'-i',str(ROOT/'tmp/frames/%05d.png'),'-frames:v',str(n),'-an','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-threads','1','-filter_threads','1','-x264-params','rc-lookahead=10:ref=1:bframes=2','-movflags','+faststart',str(out)],check=True)
 from PIL import Image
 with Image.open(ROOT/'tmp/frames/00000.png') as im:im.save(ROOT/'Taking-Turns-at-Rest.png')
 print(out)
if __name__=='__main__':main()
