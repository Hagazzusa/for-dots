"""동반 그림과 프로젝트 매니페스트를 읽기 전용으로 검사한다."""
from pathlib import Path
import json,hashlib
from PIL import Image
p=Path(__file__).resolve().parent;root=p.parent
with Image.open(p/'Third-Prize.png') as im:
 im.load();assert im.size==(1536,1024) and im.mode=='RGB'
for f in json.loads((root/'manifest.json').read_text())['files']:
 b=(root/f['path']).read_bytes()
 assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print('PNG 전체 디코드·크기·모드 및 보존 파일 해시: 통과')
