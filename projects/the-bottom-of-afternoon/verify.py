#!/usr/bin/env python3
"""최종 PNG의 무결성·크기·모드를 읽기 전용으로 검사한다."""
from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).resolve().parent
p=P/'The-Bottom-of-Afternoon.png'
with Image.open(p) as im:
 assert im.format=='PNG'
 im.verify()
with Image.open(p) as im:
 im.load()
 assert im.size==(1536,1024) and im.mode=='RGB'
print(json.dumps({'파일':p.name,'크기':[1536,1024],'색상 모드':'RGB','PNG 무결성':True,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'한계':'파일 검사는 시각 품질·건축·광학 검증을 대신하지 않습니다.'},ensure_ascii=False,indent=2))
