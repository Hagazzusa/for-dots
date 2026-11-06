"""출력과 매니페스트를 읽기 전용으로 검사한다."""
from pathlib import Path
import hashlib, json, xml.etree.ElementTree as ET
from PIL import Image
P=Path(__file__).resolve().parent
with Image.open(P/'output/Across-the-Current.png') as im:
    im.load(); assert im.size==(1100,1400)
root=ET.parse(P/'output/Across-the-Current.svg').getroot()
ns={'s':'http://www.w3.org/2000/svg'}
assert len(root.findall('.//s:g[@id="fish-1"]',ns))==1
assert len(root.findall('.//s:path',ns))==111
assert not root.findall('.//s:image',ns)
for entry in json.loads((P/'manifest.json').read_text())['files']:
    p=P/entry['path']; assert p.stat().st_size==entry['bytes']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],entry['path']
print('PNG 전체 디코드·크기, SVG 구조, 보존 파일 해시: 통과')
