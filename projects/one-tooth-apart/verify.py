"""보존 파일과 PNG를 읽기 전용으로 검사한다."""
from pathlib import Path
import hashlib,json
from PIL import Image
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
for name,record in manifest['files'].items():
 p=root/name
 assert p.stat().st_size==record['bytes'],name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],name
im=Image.open(root/'output/One-Tooth-Apart.png'); im.load()
assert im.size==(1600,1400) and im.mode in ('RGB','RGBA')
print(json.dumps({'verified_files':len(manifest['files']),'png_size':im.size,'png_mode':im.mode},ensure_ascii=False))
