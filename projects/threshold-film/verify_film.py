"""Basic encoded-file integrity checks. Visual inspection is still required."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent
p=ROOT/'Light-on-the-Threshold.mp4'
def probe():
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
d=probe();v=[s for s in d['streams'] if s['codec_type']=='video'];a=[s for s in d['streams'] if s['codec_type']=='audio']
assert len(v)==1 and not a
v=v[0];assert (v['width'],v['height'])==(640,640);assert v['r_frame_rate']=='12/1';assert int(v['nb_frames'])==144
assert abs(float(d['format']['duration'])-12)<.001
subprocess.run(['ffmpeg','-threads','2','-filter_threads','2','-v','error','-i',str(p),'-f','null','-'],check=True)
# Decode actual encoded frames around both lighting transitions, then compare luminance.
raw=subprocess.check_output(['ffmpeg','-threads','2','-filter_threads','2','-v','error','-i',str(p),'-vf','scale=32:32,format=gray','-f','rawvideo','-pix_fmt','gray','-'])
means=[sum(raw[i*1024:(i+1)*1024])/1024 for i in range(144)]
assert means[48]<means[47]-10,('off transition',means[47:50])
assert means[72]>means[71]+10,('on transition',means[71:74])
report={'duration_seconds':float(d['format']['duration']),'video_frames':int(v['nb_frames']),'fps':v['r_frame_rate'],'resolution':[v['width'],v['height']],'audio_streams':len(a),'full_decode_passed':True,'switch_off_at_seconds':4,'switch_on_at_seconds':6,'transition_frame_luma':{'before_off':means[47],'after_off':means[48],'before_on':means[71],'after_on':means[72]},'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'Pending actual encoded-frame review.'}
(ROOT/'qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
