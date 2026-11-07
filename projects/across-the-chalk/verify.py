"""보존한 생성 이미지의 구조와 파일 해시를 읽기 전용으로 검사한다."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMAGES = (
    'study/Along-the-Line.png',
    'study/Across-the-Chalk.png',
    'output/Across-the-Chalk-One-Grip.png',
)

for name in IMAGES:
    with Image.open(ROOT / name) as im:
        im.load()
        if im.format != 'PNG' or im.size != (1536, 1024) or im.mode != 'RGB':
            raise ValueError('이미지 구조 불일치: ' + name)

manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
seen = set()
for row in manifest['files']:
    name = row['path']
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or name in seen:
        raise ValueError('잘못되거나 중복된 경로: ' + name)
    seen.add(name)
    data = (ROOT / path).read_bytes()
    if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
        raise ValueError('파일 해시 불일치: ' + name)
if not set(IMAGES).issubset(seen):
    raise ValueError('이미지 매니페스트 누락')
print('PNG 세 장 전체 디코드·크기·모드·파일 해시: 통과. 작품 선정 근거와 한계는 README 참조.')
