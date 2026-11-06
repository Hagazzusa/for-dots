"""프레임 계산과 영상 인코딩을 별도 프로세스로 순서대로 실행한다."""
from pathlib import Path
import tempfile,json,subprocess,sys,argparse,os
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output-root',type=Path,default=P/'output');a=ap.parse_args();a.output_root.mkdir(parents=True,exist_ok=True)
m=json.loads((P/'model.json').read_text());env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
with tempfile.TemporaryDirectory(prefix='still-floor-frames-') as td:
 subprocess.run([sys.executable,str(P/'render_frames.py'),td],env=env,check=True)
 subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(m['fps']),'-i',str(Path(td)/'%04d.png'),'-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output_root/'A-Still-Floor.mp4')],check=True)
