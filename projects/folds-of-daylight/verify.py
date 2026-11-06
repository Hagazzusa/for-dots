"""기존 보존 파일을 바꾸지 않고 이미지와 매니페스트를 검사한다."""
from pathlib import Path
import hashlib,json
from PIL import Image
p=Path(__file__).resolve().parent
with Image.open(p/'output/Folds-of-Daylight.png') as im:
 im.load();assert im.size==(1400,1400)
for f in json.loads((p/'manifest.json').read_text())['files']:
 b=(p/f['path']).read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print('PNG 디코드·크기·보존 파일 해시: 통과')
