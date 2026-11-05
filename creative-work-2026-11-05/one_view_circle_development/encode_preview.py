from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent
frames=list((P/'preview').glob('frame_*.png'));assert len(frames)==384,len(frames)
out=P/'Passing-the-Circle-study.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_threads','2','-framerate','12','-i',str(P/'preview/frame_%04d.png'),'-vf','hqdn3d=1.5:1.5:3:3','-an','-c:v','libx264','-threads','2','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-map_metadata','-1',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(out),'-f','null','-'],check=True)
j=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));v=j['streams'][0]
assert int(v['nb_frames'])==384 and abs(float(v['duration'])-32)<1e-5
assert not any(s['codec_type']=='audio' for s in j['streams'])
(P/'preview-qa.json').write_text(json.dumps({'duration':32,'frames':384,'fps':12,'resolution':[320,320],'audio':False,'full_decode_passed':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'visual_review':'Pending'},indent=2)+'\n')
print(out)
