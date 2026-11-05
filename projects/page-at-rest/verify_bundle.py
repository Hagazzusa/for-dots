"""Preserve original PNGs; remove only private-path textual metadata from copies.
IDAT and C2PA bytes are never edited. Also audit bounded public artifacts.
"""
from pathlib import Path
import json, hashlib, struct, shutil, zipfile, zlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
PRIVATE=(b'/workspace/',b'/home/',b'/tmp/',b'C:\\Users\\')

def sha(b):return hashlib.sha256(b).hexdigest()
def chunks(data):
    assert data[:8]==b'\x89PNG\r\n\x1a\n'; i=8; result=[]
    while i<len(data):
        n=int.from_bytes(data[i:i+4],'big'); end=i+n+12
        t=data[i+4:i+8]; content=data[i+8:i+8+n]
        assert end<=len(data)
        assert zlib.crc32(t+content)&0xffffffff==int.from_bytes(data[i+8+n:end],'big')
        result.append((t,content,data[i:end]));i=end
    return result

reports=[]
for path in sorted((ROOT/'renders').glob('*.png')):
    # Content-address original versions: rerendering the same filename must not
    # accidentally restore an older image during another verification pass.
    incoming=path.read_bytes()
    original=ROOT/'private_originals'/path.relative_to(ROOT).parent/(path.stem+'_'+sha(incoming)[:16]+path.suffix)
    original.parent.mkdir(parents=True,exist_ok=True)
    if not original.exists():shutil.copy2(path,original)
    data=incoming; cs=chunks(data); output=data[:8]; removed=[]
    for t,c,raw in cs:
        # Keep provenance including all caBX content; reject unknown private data.
        if t in (b'tEXt',b'iTXt',b'zTXt'):
            decoded=c
            if t==b'zTXt':
                try:decoded=zlib.decompress(c.split(b'\0',1)[1][1:])
                except Exception:pass
            if any(s in decoded for s in PRIVATE):removed.append(t.decode());continue
        output+=raw
    path.write_bytes(output)
    assert not any(p in output for p in PRIVATE), 'private path bytes remain in PNG'
    out=chunks(output)
    idat=sha(b''.join(c for t,c,_ in cs if t==b'IDAT'))
    assert idat==sha(b''.join(c for t,c,_ in out if t==b'IDAT'))
    assert [c for t,c,_ in cs if t==b'caBX']==[c for t,c,_ in out if t==b'caBX']
    assert Image.open(path).tobytes()==Image.open(original).tobytes()
    im=Image.open(path).convert('RGB'); vals=list(im.get_flattened_data() if hasattr(im,'get_flattened_data') else im.getdata()); total=len(vals)
    report={'file':str(path.relative_to(ROOT)),'private_text_chunks_removed':removed,'idat_sha256':idat,
            'identical_decoded_pixels':True,'c2pa_present':any(t==b'caBX' for t,_,_ in cs),'c2pa_unchanged':True,
            'size':list(im.size),'all_channels_at_255_fraction':sum(v==(255,255,255) for v in vals)/total,
            'any_channel_at_255_fraction':sum(max(v)==255 for v in vals)/total}
    reports.append(report)

concept=ROOT/'reference/gpt_image_concept.png'; c=chunks(concept.read_bytes())
concept_report={'file':str(concept.relative_to(ROOT)),'sha256':sha(concept.read_bytes()),
                'c2pa_present':any(t==b'caBX' for t,_,_ in c),
                'c2pa_sha256':sha(b''.join(d for t,d,_ in c if t==b'caBX'))}
assert concept_report['c2pa_present']
assert not any(p in concept.read_bytes() for p in PRIVATE)
with zipfile.ZipFile(ROOT/'cad/A_Page_at_Rest.FCStd') as z:
    assert not any(p in z.read('Document.xml') for p in PRIVATE)
assert not any(p in (ROOT/'A_Page_at_Rest.blend').read_bytes() for p in PRIVATE)
summary={'scope':'metadata integrity, pixel clipping counts and bounded file dependencies; not safety certification',
         'renders':reports,'concept':concept_report,'fcstd_document_has_no_private_paths':True,
         'blend_has_no_private_path_bytes':True}
(ROOT/'bundle_validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
