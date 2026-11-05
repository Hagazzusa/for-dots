#!/usr/bin/env python3
"""보존한 PNG를 읽기 전용으로 검사한다."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent
EXPECTED='46629d164af5e04b76fc2e3ec281825c2d04610f1add93447b0c3c0b98ce866f'
def verify():
 p=ROOT/'The-Low-Corner.png'
 with Image.open(p) as im:
  assert im.format=='PNG';im.verify()
 with Image.open(p) as im:
  im.load();assert im.size==(1536,1024) and im.mode=='RGB'
  extrema=im.getextrema();assert all(hi>lo for lo,hi in extrema)
 h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==EXPECTED
 assert (ROOT/'prompt.txt').read_text(encoding='utf-8').strip()
 return {'파일':p.name,'형식':'PNG','크기':[1536,1024],'모드':'RGB','바이트':p.stat().st_size,'SHA256':h,'전체 픽셀 디코드':True,'채널 범위':extrema,'한계':'파일 무결성 검사입니다. 장면의 표현과 구도는 별도로 육안 검토합니다.'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--report',type=Path);a=ap.parse_args();s=json.dumps(verify(),ensure_ascii=False,indent=2)+'\n'
 if a.report:a.report.write_text(s,encoding='utf-8')
 print(s,end='')
if __name__=='__main__':main()
