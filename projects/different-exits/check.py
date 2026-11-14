"""읽기 전용 구조 검사와 임시 디렉터리 재생성 대조."""
from pathlib import Path
import tempfile, shutil, subprocess, hashlib, xml.etree.ElementTree as ET
from PIL import Image
p=Path(__file__).resolve().parent
root=ET.parse(p/'Different-Exits.svg').getroot()
ns={'s':'http://www.w3.org/2000/svg'}
assert len(root.findall('s:path',ns))==17
assert len(root.findall('s:circle',ns))==1
with Image.open(p/'Different-Exits.png') as im:
    im.load(); assert im.size==(1200,1500)
with tempfile.TemporaryDirectory() as t:
    q=Path(t); shutil.copy(p/'make.py',q/'make.py')
    subprocess.run(['python3',str(q/'make.py')],check=True)
    subprocess.run(['inkscape',str(q/'Different-Exits.svg'),'--export-filename='+str(q/'Different-Exits.png')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for name in ['Different-Exits.svg','Different-Exits.png']:
        assert (p/name).read_bytes()==(q/name).read_bytes(),name
        print(name,hashlib.sha256((p/name).read_bytes()).hexdigest())
print('PASS: 17 arcs, 1 circle, 1200x1500 PNG; SVG and PNG identical on regeneration')
