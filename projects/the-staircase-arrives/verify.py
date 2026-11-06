"""생성 원본과 보존 자료를 변경하지 않고 검사한다."""
from pathlib import Path
import json,hashlib
from PIL import Image
root=Path(__file__).resolve().parent
files=json.loads((root/'manifest.json').read_text())['files']
for name,record in files.items():
 p=root/name
 assert p.stat().st_size==record['bytes'],name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],name
im=Image.open(root/'output/The-Staircase-Arrives.png');im.load()
assert im.size==(1122,1402) and im.mode=='RGB'
print(json.dumps({'files_checked':len(files),'png_size':im.size,'mode':im.mode,'note':'장면 내용과 미적 판단은 자동 검사 대상이 아닙니다.'},ensure_ascii=False))
