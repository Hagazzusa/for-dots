"""네이티브 시야 렌더 두 장을 훼손하지 않고 나란히 배치한다."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent;out=ROOT/'output'
# 네이티브 렌더 픽셀은 그대로 두고 작업 경로 등 메타데이터만 제거한다.
from PIL import Image
for name in ['left.png','right.png','assembled.png']:
 im=Image.open(out/name); im.load(); clean=Image.new(im.mode,im.size); clean.putdata(list(im.getdata())); clean.save(out/name)
s='''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1800" height="1090" viewBox="0 0 1800 1090">
<rect width="1800" height="1090" fill="#f2ecdf"/>
<g fill="#293837" font-family="Noto Sans CJK KR, sans-serif">
<text x="70" y="82" font-size="44">한 짝의 뒤편</text>
<text x="70" y="142" font-size="24">왼쪽 창</text><text x="930" y="142" font-size="24">오른쪽 창</text>
<image x="70" y="170" width="800" height="800" xlink:href="left.png"/>
<image x="930" y="170" width="800" height="800" xlink:href="right.png"/>
<text x="70" y="1030" font-size="25">같은 상자, 다른 자리. 두 줄의 바늘땀은 그대로.</text>
</g></svg>'''
(out/'The-Other-Shoe.svg').write_text(s+'\n')
subprocess.run(['inkscape',str(out/'The-Other-Shoe.svg'),'--export-filename='+str(out/'The-Other-Shoe.png')],check=True)
