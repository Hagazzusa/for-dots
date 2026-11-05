from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
for f in range(1,97):assert (ROOT/'frames'/f'frame_{f:04d}.png').is_file(),f
subprocess.run(['ffmpeg','-y','-threads','2','-filter_threads','2','-framerate','12','-start_number','1','-i',str(ROOT/'frames/frame_%04d.png'),'-frames:v','96','-an','-vf','hqdn3d=1.5:1.5:3:3','-c:v','libx264','-threads','2','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart','-map_metadata','-1',str(ROOT/'One-View-Circle.mp4')],check=True)
