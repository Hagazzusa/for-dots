#!/usr/bin/env python3
"""두 연구를 재생성하고 비교 이미지를 만든다. 기존 결과를 보존하려면 별도 사본에서 실행한다."""
from pathlib import Path
import subprocess,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for script in ['build_lines.py','build_cut.py']:subprocess.run([sys.executable,str(ROOT/script)],check=True)
canvas=Image.new('RGB',(1800,1100),'#eee9df');d=ImageDraw.Draw(canvas)
for row,stem in enumerate(['study','cut']):
 for col in range(3):
  p=ROOT/'output'/f'{stem}-{col+1}.png'
  with Image.open(p) as image:
   image.thumbnail((580,500),Image.Resampling.LANCZOS);canvas.paste(image,(col*600+(600-image.width)//2,row*550+35))
  d.text((col*600+25,row*550+15),f'{"A" if row==0 else "B"}{col+1}',fill='#273c40')
canvas.save(ROOT/'output'/'comparison.png')
