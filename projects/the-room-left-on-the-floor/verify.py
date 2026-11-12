"""보존 파일의 크기·해시와 원문 기본 형식을 읽기 전용 검사한다."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
for row in manifest['files']:
    path = root / row['path']
    assert path.is_file() and not path.is_symlink(), row['path']
    data = path.read_bytes()
    assert len(data) == row['size'], row['path']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
text = (root / 'story.md').read_text(encoding='utf-8')
assert text.startswith('# 남은 평면도\n\n')
assert text.endswith('\n') and '\ufffd' not in text
assert len(text.split('\n\n')) > 20
print('PASS: 원문 기본 형식과 보존 파일 바이트')
