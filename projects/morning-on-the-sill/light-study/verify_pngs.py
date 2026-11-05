"""PNG 공개본의 경로 메타데이터와 픽셀 보존 검사. Pillow 필요.
기본 모드는 읽기 전용이다. --sanitize는 최초 공개본과 보고서를 기록한다.
이미지 노이즈 억제·색 보정·재인코딩은 하지 않는다.
"""
from pathlib import Path
from io import BytesIO
import argparse,hashlib,json,struct,zlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
REPORT=ROOT/'png_validation.json'
PRIVATE=(b'/' + b'workspace/',b'/' + b'home/',b'/' + b'tmp/')
NAMES=['low_side_morning.png','higher_side_morning.png','soft_overcast_comparison.png']
def sha(b):return hashlib.sha256(b).hexdigest()
def chunks(data):
 assert data[:8]==b'\x89PNG\r\n\x1a\n';at=8;out=[]
 while at<len(data):
  n=struct.unpack_from('>I',data,at)[0];end=at+12+n;assert end<=len(data)
  kind=data[at+4:at+8];body=data[at+8:at+8+n]
  assert zlib.crc32(kind+body)&0xffffffff==struct.unpack_from('>I',data,at+8+n)[0]
  out.append((kind,body,data[at:end]));at=end
 assert at==len(data) and out[-1][0]==b'IEND';return out
def text_payload(kind,body):
 if kind==b'tEXt':return body
 if kind==b'zTXt':
  key,rest=body.split(b'\0',1);assert rest[0]==0;return key+b'\0'+zlib.decompress(rest[1:])
 if kind==b'iTXt':
  key,flag,method,language,translated,content=body.split(b'\0',5)
  assert flag in (b'',b'\x01') and method in (b'',b'\x00')
  return key+b'\0'+language+b'\0'+translated+b'\0'+(zlib.decompress(content) if flag==b'\x01' else content)
 return b''
def no_private(data,cs):
 assert not any(t in data for t in PRIVATE)
 assert not any(t in text_payload(k,b) for k,b,_ in cs for t in PRIVATE)
def idat(cs):return b''.join(b for k,b,_ in cs if k==b'IDAT')
def pixels(data):
 im=Image.open(BytesIO(data));im.load();assert im.size==(600,400);return im.mode,im.tobytes()
def verify_saved():
 d=json.loads(REPORT.read_text());assert len(d['files'])==3
 for r in d['files']:
  data=(ROOT/r['file']).read_bytes();cs=chunks(data);no_private(data,cs);mode,px=pixels(data)
  assert sha(data)==r['public_sha256'] and sha(idat(cs))==r['idat_sha256']
  assert mode==r['mode'] and sha(px)==r['decoded_pixel_sha256']
 print('읽기 전용 검사 통과: 공개 PNG 3개와 기록된 해시·IDAT·픽셀 일치')
ap=argparse.ArgumentParser();ap.add_argument('--sanitize',action='store_true');args=ap.parse_args()
if REPORT.exists():
 verify_saved()
else:
 assert args.sanitize,'검사 보고서가 없습니다. 작업 사본에서 최초 --sanitize가 필요합니다'
 prepared=[];records=[]
 for name in NAMES:
  p=ROOT/'renders'/name;raw=p.read_bytes();before=chunks(raw);removed=[];kept=[]
  for k,b,packet in before:
   if any(t in text_payload(k,b) for t in PRIVATE):removed.append(k.decode());continue
   kept.append(packet)
  clean=raw[:8]+b''.join(kept);after=chunks(clean);no_private(clean,after)
  assert idat(before)==idat(after)
  assert [b for k,b,_ in before if k==b'caBX']==[b for k,b,_ in after if k==b'caBX']
  mode,px=pixels(raw);out_mode,out_px=pixels(clean);assert mode==out_mode and px==out_px
  prepared.append((p,raw,clean))
  records.append({'file':str(p.relative_to(ROOT)),'input_sha256':sha(raw),'public_sha256':sha(clean),'removed_private_text_chunks':removed,'idat_sha256':sha(idat(before)),'decoded_pixel_sha256':sha(px),'mode':mode,'dimensions':[600,400],'idat_unchanged':True,'decoded_pixels_unchanged':True,'c2pa_unchanged_if_present':True})
 for p,raw,clean in prepared:
  backup=ROOT/'private_originals'/(p.stem+'_'+sha(raw)[:16]+'.png');backup.parent.mkdir(exist_ok=True)
  if backup.exists():assert backup.read_bytes()==raw
  else:backup.write_bytes(raw)
  p.write_bytes(clean)
 REPORT.write_text(json.dumps({'scope':'실제 PNG 세 장의 경로 텍스트 제거와 IDAT·디코딩 픽셀 보존을 확인한 기록. 일반 보안 인증이나 이미지 노이즈 처리 아님','default_check_read_only':True,'files':records},ensure_ascii=False,indent=2)+'\n')
 verify_saved()
