"""Encoded output checks; visual review must be recorded separately."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent;movie=ROOT/'One-View-Circle.mp4'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]));v=[s for s in d['streams'] if s['codec_type']=='video'];a=[s for s in d['streams'] if s['codec_type']=='audio'];assert len(v)==1 and not a
v=v[0];assert (v['width'],v['height'])==(640,640) and v['r_frame_rate']=='12/1' and int(v['nb_frames'])==96
assert abs(float(d['format']['duration'])-8)<.001
subprocess.run(['ffmpeg','-threads','2','-filter_threads','2','-v','error','-i',str(movie),'-f','null','-'],check=True)
frames=ROOT/'frames';digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert len(list(frames.glob('frame_*.png')))==96
assert len({digest(frames/f'frame_{i:04d}.png') for i in range(1,25)})==1
assert len({digest(frames/f'frame_{i:04d}.png') for i in range(72,97)})==1
assert len({digest(frames/f'frame_{i:04d}.png') for i in range(25,73)})==48
revision=json.loads((ROOT/'frame_revision.json').read_text());assert revision['source_sha256']==digest(ROOT/'build.py')
q={'duration_seconds':8,'frames':96,'resolution':[640,640],'fps':12,'audio_streams':0,'full_decode_passed':True,'held_source_frames_verified':True,'moving_source_frames_distinct':48,'frame_revision_matches_source':True,'sha256':digest(movie),'projection_check':json.loads((ROOT/'projection_check.json').read_text()),'visual_review':'Pending encoded-frame inspection.'};(ROOT/'qa.json').write_text(json.dumps(q,indent=2)+'\n');print('Encoded file and frame cache checks passed.')
