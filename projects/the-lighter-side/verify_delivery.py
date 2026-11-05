"""Verify encoded media, source-frame continuity, framing and the stored geometry QA."""
from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from PIL import Image
from mobile import state,PERIOD,FPS,WIDTH,HEIGHT,CAMERA,TARGET,SCALE
from soft_renderer import render_meshes
P=Path(__file__).resolve().parent;movie=P/'The-Lighter-Side.mp4';frames=P/'tmp/frames';count=round(PERIOD*FPS)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
video=[s for s in probe['streams'] if s['codec_type']=='video'];assert len(video)==1 and len(probe['streams'])==1
v=video[0];assert v['width']==WIDTH and v['height']==HEIGHT and v['r_frame_rate']==f'{FPS}/1' and int(v['nb_frames'])==count
assert abs(float(probe['format']['duration'])-PERIOD)<1e-6
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(movie),'-f','null','-'],check=True)
first=None;previous=None;differences=[]
for k in range(count):
 with Image.open(frames/f'{k:04d}.png') as im:
  assert im.size==(WIDTH,HEIGHT) and im.mode=='RGB';a=np.array(im,dtype=np.int16)
 if first is None:first=a.copy()
 if previous is not None:differences.append(float(np.abs(a-previous).mean()))
 previous=a
assert min(differences)>0
seam_difference=float(np.abs(previous-first).mean())
assert seam_difference<max(differences)*1.2
end=np.asarray(render_meshes(state(PERIOD)[0],WIDTH,HEIGHT,CAMERA,TARGET,SCALE,supersample=2),dtype=np.int16)
assert np.max(np.abs(end-first))==0,'Virtual endpoint differs from first frame'
# Match renderer camera basis; disregard only the intentionally cropped ceiling thread.
eye=np.array(CAMERA);target=np.array(TARGET);forward=target-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);margin=1.
for t in np.linspace(0,PERIOD,385):
 vs=np.vstack([m['vertices'] for m in state(t)[0][1:]]);x=.5+(vs-eye)@right/(SCALE*WIDTH/HEIGHT);y=.5+(vs-eye)@up/SCALE
 margin=min(margin,float(np.min([x.min(),1-x.max(),y.min(),1-y.max()])))
assert margin>.07
geometry=json.loads((P/'geometry-qa.json').read_text())
assert geometry['passed'] and not geometry['failures']
assert geometry['source_sha256']==hashlib.sha256((P/'mobile.py').read_bytes()).hexdigest()
from collections import Counter
for mesh in state(8.)[0]:
 edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in mesh['faces'] for i in range(3));assert set(edges.values())=={2}
assert (P/'The-Lighter-Side.png').read_bytes()==(frames/'0192.png').read_bytes()
obj=(P/'The-Lighter-Side.obj').read_text().splitlines();verts=[x for x in obj if x.startswith('v ')];faces=[x for x in obj if x.startswith('f ')]
assert len(verts)==sum(len(x['vertices']) for x in state(8.)[0])
assert len(faces)==sum(len(x['faces']) for x in state(8.)[0])
assert all(1<=int(v)<=len(verts) for f in faces for v in f.split()[1:])
assert 'mtllib The-Lighter-Side.mtl' in obj and (P/'The-Lighter-Side.mtl').exists()
# Preserve the exact geometry report while recording the media checks separately.
report={'title':'가벼운 쪽의 거리','duration_seconds':PERIOD,'frames':count,'fps':FPS,'dimensions':[WIDTH,HEIGHT],'audio_streams':0,'full_decode_passed':True,'all_source_frames_verified':True,'all_consecutive_frames_change':True,'adjacent_frame_mean_absolute_difference_8bit':{'min':min(differences),'max':max(differences),'median':float(np.median(differences)),'loop_boundary':seam_difference},'virtual_endpoint_pixel_identical_to_first':True,'minimum_normalized_frame_margin_except_ceiling_thread':margin,'geometry_report':'geometry-qa.json','visual_review':'Encoded sample frames and source motion sequence inspected; normal-speed playback was not available.','limits':'Prescribed animation with sampled static geometry checks; not wind dynamics or a fabrication test.'}
(P/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
