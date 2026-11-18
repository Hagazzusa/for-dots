from pathlib import Path
import tempfile, subprocess, shutil
from PIL import Image
p=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as d:
 q=Path(d); shutil.copy(p/'make.py',q/'make.py')
 subprocess.run(['python3',str(q/'make.py')],check=True)
 subprocess.run(['inkscape',str(q/'Pocket-Observatory.svg'),'--export-filename='+str(q/'Pocket-Observatory.png')],check=True,capture_output=True)
 for ext in ('svg','png'):
  f='Pocket-Observatory.'+ext
  assert (p/f).read_bytes()==(q/f).read_bytes(),f
assert Image.open(p/'Pocket-Observatory.png').size==(1200,1400)
print('SVG·PNG 재생성 바이트 일치 및 크기 확인')
