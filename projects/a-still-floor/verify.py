"""정지 그림·광선밀도·영상 전체 디코드·표본 프레임·파일 해시를 검사한다."""
from pathlib import Path
import json,subprocess,sys,tempfile,argparse,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preview-dir',type=Path);args=ap.parse_args()
 m=json.loads((P/'model.json').read_text());video=P/'output/A-Still-Floor.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
 assert len(probe['streams'])==1 and probe['streams'][0]['codec_type']=='video'
 stream=probe['streams'][0];n=m['video_pixels_per_axis'];frames=round(m['loop_seconds']*m['fps'])
 assert stream['width']==n and stream['height']==n and stream['r_frame_rate']=='24/1';assert int(stream['nb_frames'])==frames
 assert abs(float(probe['format']['duration'])-m['loop_seconds'])<.001
 with tempfile.TemporaryDirectory(prefix='still-floor-check-') as td:
  raw=Path(td)/'frames.rgb'
  subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(video),'-map','0:v:0','-threads','1','-pix_fmt','rgb24','-f','rawvideo',str(raw)],check=True)
  assert raw.stat().st_size==frames*n*n*3
  import numpy as np
  from PIL import Image,ImageDraw,ImageFont
  from build import irradiance,colorize
  changes=[];selected={};previews=[];first=previous=None
  with raw.open('rb') as f:
   for i in range(frames):
    b=f.read(n*n*3);assert len(b)==n*n*3;img=np.frombuffer(b,dtype=np.uint8).reshape(n,n,3)
    if first is None:first=img.copy()
    if previous is not None:changes.append(float(np.mean(np.abs(img.astype(np.int16)-previous.astype(np.int16)))))
    previous=img.copy()
    if i in (0,60,120,180,239):selected[i]=img.copy()
    if args.preview_dir and i%24==0:
     thumbnail=Image.fromarray(img).resize((240,240));tile=Image.new('RGB',(240,264),'white');tile.paste(thumbnail,(0,24));ImageDraw.Draw(tile).text((8,4),f'{i/24:.0f}s',fill='black',font=ImageFont.load_default(size=16));previews.append(tile)
  seam=float(np.mean(np.abs(first.astype(np.int16)-previous.astype(np.int16))))
  assert min(changes)>0 and seam<max(changes)*1.5
  errors={}
  for i,actual in selected.items():
   I,total=irradiance(i/m['fps'],m,m['video_rays_per_axis'],n);expected=colorize(I);err=float(np.mean(np.abs(actual.astype(np.int16)-expected.astype(np.int16))));assert err<2.0,(i,err);errors[str(i)]=err
  I0,_=irradiance(0,m,m['video_rays_per_axis'],n);I10,_=irradiance(m['loop_seconds'],m,m['video_rays_per_axis'],n);assert np.array_equal(I0,I10)
  if args.preview_dir:
   args.preview_dir.mkdir(parents=True,exist_ok=True);sheet=Image.new('RGB',(1200,528),'white')
   for j,tile in enumerate(previews):sheet.paste(tile,((j%5)*240,(j//5)*264))
   sheet.save(args.preview_dir/'contact-sheet.png')
 with Image.open(P/'output/A-Still-Floor.png') as im:
  im.load();assert im.size==(m['still_pixels_per_axis'],)*2 and im.mode=='RGB';still=np.array(im)
 with np.load(P/'output/irradiance.npz') as data:field=data['intensity'];assert field.shape==still.shape[:2] and np.isfinite(field).all() and field.min()>=0 and abs(float(field.mean())-1)<1e-6
 assert np.max(np.abs(colorize(field).astype(np.int16)-still.astype(np.int16)))<=1
 manifest=P/'manifest.json'
 if manifest.exists():
  for entry in json.loads(manifest.read_text())['files']:
   b=(P/entry['path']).read_bytes();assert len(b)==entry['bytes'] and hashlib.sha256(b).hexdigest()==entry['sha256'],entry['path']
 report={'영상 프레임 수':frames,'초당 프레임':m['fps'],'영상 크기':[n,n],'영상 길이 초':float(probe['format']['duration']),'오디오 트랙':False,'전체 프레임 디코드':True,'소스 대비 압축 프레임 평균 절대 오차 0~255':errors,'인접 프레임 평균 절대 차이 범위':[min(changes),max(changes)],'끝에서 처음 평균 절대 차이':seam,'0초·10초 소스 강도 배열 완전 일치':True,'정지 강도 평균':float(field.mean()),'정지 PNG 전체 디코드':True,'한계':'정상 속도 실시간 재생 육안 확인은 하지 않았습니다. 프레임 표본·디코드·수치 비교는 체감 움직임 평가를 대신하지 않습니다.'}
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
