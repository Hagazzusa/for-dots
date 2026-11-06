"""만화 PNG와 보존 파일 해시를 읽기 전용으로 검사한다."""
from pathlib import Path
import json,hashlib
from PIL import Image
p=Path(__file__).resolve().parent
with Image.open(p/'output/The-Unfolded-Map.png') as im:
 im.load();assert im.size==(1122,1402) and im.mode=='RGB'
for f in json.loads((p/'manifest.json').read_text())['files']:
 b=(p/f['path']).read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print('PNG 전체 디코드·크기·색상 모드·보존 파일 해시: 통과')
