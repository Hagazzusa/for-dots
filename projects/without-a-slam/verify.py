"""희곡 원문·PDF 글자·조판·글꼴·보존 파일을 읽기 전용으로 검사한다."""
from pathlib import Path
from collections import defaultdict
import re, json, hashlib
import pdfplumber
from pypdf import PdfReader
p=Path(__file__).resolve().parent
raw=(p/'play.txt').read_bytes();source=raw.decode()
assert (p/'output/text/Without-a-Slam.txt').read_bytes()==raw
reader=PdfReader(p/'output/pdf/Without-a-Slam.pdf')
assert reader.metadata.title==source.splitlines()[0]
actual=[]
with pdfplumber.open(p/'output/pdf/Without-a-Slam.pdf') as pdf:
    for i,page in enumerate(pdf.pages):
        assert (page.width,page.height)==(520,740)
        rows=defaultdict(list)
        for ch in page.chars:
            if ch['top']>690:continue
            assert ch['text'] not in ('\ufffd','\x00')
            assert 55.9<=ch['x0']<ch['x1']<=464.1
            assert 45<ch['top']<ch['bottom']<685
            assert 'WithoutASlamNotoSerifKR' in ch['fontname']
            rows[round(ch['top'],3)].append(ch)
        prev=0
        for top,chars in sorted(rows.items()):
            assert top>prev;prev=max(x['bottom'] for x in chars)
            chars.sort(key=lambda x:x['x0'])
            assert all(a['x1']<=b['x0']+.1 for a,b in zip(chars,chars[1:]))
            actual.append(''.join(x['text'] for x in chars))
        for ref in reader.pages[i]['/Resources']['/Font'].get_object().values():
            f=ref.get_object()
            if 'WithoutASlam' in str(f.get('/BaseFont','')):
                assert '/FontFile2' in f['/FontDescriptor'].get_object() and '/ToUnicode' in f
clean=lambda x:re.sub(r'\s+','',x)
assert clean(''.join(actual))==clean(source)
if (p/'manifest.json').exists():
    for f in json.loads((p/'manifest.json').read_text())['files']:
        b=(p/f['path']).read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
print(json.dumps({'PDF 쪽 수':len(reader.pages),'PDF 원문 글자 일치':True,'TXT 바이트 일치':True,'경계·겹침·내장 글꼴':True},ensure_ascii=False,indent=2))
