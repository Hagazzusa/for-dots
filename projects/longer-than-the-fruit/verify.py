"""원본 PNG의 바이트와 전체 디코드를 읽기 전용으로 검사합니다."""
from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).resolve().parent
EXPECTED='1a07c4736f735bd62be66c8ceaf41ab4997f159848d7c1991a479690e8e9ad9d'

def verify():
 p=P/'Longer-Than-the-Fruit.png';raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==EXPECTED
 with Image.open(p) as im:
  im.load();assert im.format=='PNG' and im.size==(1454,1082) and im.mode=='RGB'
  size=list(im.size);mode=im.mode
 return {'제목':'사과보다 긴 것','파일':p.name,'크기':size,'모드':mode,'바이트':len(raw),'SHA256':sha,'전체 PNG 디코드':True,'생성 원본과 바이트 일치':True,'한계':'원본 보존과 파일 유효성 검사입니다. 같은 지시문으로 동일 픽셀의 재생성을 보장하지 않습니다.'}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
