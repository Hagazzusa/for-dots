#!/usr/bin/env python3
"""모델 표본·에너지·영상 디코드와 대표 프레임을 읽기 전용으로 검사한다."""
from pathlib import Path
import argparse,json,subprocess
import numpy as np
from model import ROOT,parameters,geometry,energy,integrate
from render import frame

def verify():
 p=parameters();rows=np.loadtxt(ROOT/'motion.csv',delimiter=',',skiprows=1);n=p['duration_s']*p['fps']
 assert rows.shape==(n,5) and np.isfinite(rows).all()
 assert np.max(abs(rows[:,0]-np.arange(n)/p['fps']))<1e-9
 energies=np.array([energy(row[1:],p) for row in rows]);relative=float(np.max(abs(energies/energies[0]-1)))
 assert relative<1e-8
 regenerated=integrate(p).sol(rows[:,0]).T
 assert np.max(abs(regenerated-rows[:,1:]))<1e-8
 lengths=[];separations=[]
 for row in rows:
  anchors,bobs,links=geometry(row[[1,3]],p)
  assert np.allclose(np.linalg.norm(bobs-anchors,axis=1),p['length_m'],atol=1e-12)
  assert np.allclose(np.linalg.norm(links-anchors,axis=1),p['length_m']*p['spring_fraction'],atol=1e-12)
  lengths.append(np.linalg.norm(links[1]-links[0]));separations.append(np.linalg.norm(bobs[1]-bobs[0]))
 video=ROOT/'Taking-Turns-at-Rest.mp4'
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
 assert len(metadata['streams'])==1
 stream=metadata['streams'][0];assert stream['codec_type']=='video' and stream['codec_name']=='h264'
 assert (stream['width'],stream['height'])==(p['width'],p['height'])
 assert stream['r_frame_rate']==f"{p['fps']}/1" and int(stream['nb_read_frames'])==n
 assert abs(float(metadata['format']['duration'])-p['duration_s'])<.01
 proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(video),'-an','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-filter_threads','1','pipe:1'],stdout=subprocess.PIPE)
 frame_bytes=p['width']*p['height']*3;count=0;previous=None;max_step=0;sample_errors={};samples={0,round(8.9*p['fps']),round(17.7*p['fps']),n-1}
 while True:
  data=proc.stdout.read(frame_bytes)
  if not data:break
  assert len(data)==frame_bytes
  pixels=np.frombuffer(data,np.uint8).reshape(p['height'],p['width'],3)
  if previous is not None:max_step=max(max_step,float(np.mean(abs(pixels.astype(float)-previous))))
  if count in samples:
   expected=np.asarray(frame(rows[count,1:],p,rows[count,0],True),dtype=float)
   error=float(np.mean(abs(pixels.astype(float)-expected)));assert error<3
   sample_errors[str(count)]=error
  previous=pixels.astype(np.int16);count+=1
 assert proc.wait()==0 and count==n and max_step>0
 return {'영상':{'초':p['duration_s'],'fps':p['fps'],'프레임':count,'크기':[p['width'],p['height']],'무음':True,'최대 인접 프레임 평균 변화':max_step,'대표 프레임 원본 대비 평균 오차_255기준':sample_errors},'모델':{'총에너지 최대 상대 변화':relative,'적분 재생성 최대 상태 차이':float(np.max(abs(regenerated-rows[:,1:]))),'연결점 거리 범위_m':[float(min(lengths)),float(max(lengths))],'두 질점 최소 거리_m':float(min(separations))},'한계':'이상화된 평면 모델·파일 디코드 검사입니다. 실제 제작·안전·정상 속도 육안 재생 검증은 아닙니다.'}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--report',type=Path);args=ap.parse_args();s=json.dumps(verify(),ensure_ascii=False,indent=2)+'\n'
 if args.report:args.report.write_text(s)
 print(s)
if __name__=='__main__':main()
