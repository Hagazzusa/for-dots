"""Encode only after Blender exits; keep memory usage bounded."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
frames=ROOT/'frames'
for i in range(1,145):
 assert (frames/f'frame_{i:04d}.png').is_file(),i
subprocess.run(['ffmpeg','-y','-threads','2','-filter_threads','2','-framerate','12','-start_number','1','-i',str(frames/'frame_%04d.png'),'-frames:v','144','-an','-vf','hqdn3d=1.5:1.5:3:3','-c:v','libx264','-threads','2','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart','-map_metadata','-1',str(ROOT/'Light-on-the-Threshold.mp4')],check=True)
