"""보존한 생성 이미지의 구조와 파일 해시를 읽기 전용으로 검사한다."""
from pathlib import Path
import json, hashlib
from PIL import Image
p=Path(__file__).resolve().parent
for name in ('Along-the-Line.png','Across-the-Chalk.png'):
    with Image.open(p/'study'/name) as im:
        im.load()
        assert im.size==(1536,1024) and im.mode=='RGB'
for f in json.loads((p/'manifest.json').read_text())['files']:
    b=(p/f['path']).read_bytes()
    assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print('PNG 두 장 전체 디코드·크기·모드·파일 해시: 통과. 작품 완성도 판정은 별도 검토 기록 참조.')
