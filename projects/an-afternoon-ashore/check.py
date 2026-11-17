"""원본을 덮어쓰지 않고 구조, PNG, 동일 환경 재생성을 검사합니다."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parent
svg=ROOT/'An-Afternoon-Ashore.svg'
png=ROOT/'An-Afternoon-Ashore.png'
root=ET.parse(svg).getroot()
assert root.attrib['viewBox']=='0 0 1440 1080'
assert not root.findall('.//{http://www.w3.org/2000/svg}image')
assert not root.findall('.//{http://www.w3.org/2000/svg}script')
with Image.open(png) as im:
    assert im.size==(1440,1080)
    assert im.mode in ('RGB','RGBA')
    assert im.getpixel((0,0))[:3]==(243,237,219)
    assert len(im.getcolors(im.width*im.height))>100
with tempfile.TemporaryDirectory() as d:
    p=Path(d)
    shutil.copyfile(ROOT/'make.py',p/'make.py')
    subprocess.run(['python3',str(p/'make.py')],check=True)
    subprocess.run(['inkscape',str(p/svg.name),'--export-filename='+str(p/png.name)],check=True,capture_output=True)
    for original in (svg,png):
        assert original.read_bytes()==(p/original.name).read_bytes(), original.name
        print(original.name, hashlib.sha256(original.read_bytes()).hexdigest())
print('구조·해상도·동일 환경 바이트 재생성 검사 통과')
