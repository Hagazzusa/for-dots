"""Keep original PNGs, remove private path text from public copies, compare pixels.
This writes sanitized PNGs and QA JSON; it is not a read-only check. Pillow needed.
"""
from pathlib import Path
import json,hashlib,zlib,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent
PRIVATE=(b'/' + b'workspace/',b'/' + b'home/',b'/' + b'tmp/')
def sha(data):return hashlib.sha256(data).hexdigest()
def chunks(data):
 assert data[:8]==b'\x89PNG\r\n\x1a\n';i=8;out=[]
 while i<len(data):
  n=int.from_bytes(data[i:i+4],'big');end=i+n+12;t=data[i+4:i+8];body=data[i+8:i+8+n]
  assert end<=len(data) and zlib.crc32(t+body)&0xffffffff==int.from_bytes(data[i+8+n:end],'big')
  out.append((t,body,data[i:end]));i=end
 return out
records=[]
for p in sorted((ROOT/'renders').glob('*.png')):
 original_bytes=p.read_bytes();original=ROOT/'private_originals'/p.relative_to(ROOT).parent/(p.stem+'_'+sha(original_bytes)[:16]+p.suffix)
 original.parent.mkdir(parents=True,exist_ok=True)
 if not original.exists():original.write_bytes(original_bytes)
 source=chunks(original_bytes);clean=original_bytes[:8];removed=[]
 for t,b,raw in source:
  if t in (b'tEXt',b'iTXt',b'zTXt') and any(x in b for x in PRIVATE):removed.append(t.decode());continue
  clean+=raw
 assert not any(x in clean for x in PRIVATE)
 p.write_bytes(clean);out=chunks(clean)
 idat=lambda cs:b''.join(b for t,b,_ in cs if t==b'IDAT')
 c2pa=lambda cs:[b for t,b,_ in cs if t==b'caBX']
 assert idat(source)==idat(out) and c2pa(source)==c2pa(out)
 im=Image.open(p);assert im.tobytes()==Image.open(original).tobytes()
 rgb=im.convert('RGB');pixels=list(rgb.get_flattened_data() if hasattr(rgb,'get_flattened_data') else rgb.getdata());N=len(pixels)
 records.append({'file':str(p.relative_to(ROOT)),'size':list(im.size),'private_text_chunks_removed':removed,
                 'idat_sha256':sha(idat(source)),'identical_idat':True,'identical_decoded_pixels':True,
                 'c2pa_present':bool(c2pa(source)),'c2pa_unchanged':True,
                 'all_channels_255_fraction':sum(p==(255,255,255) for p in pixels)/N,
                 'any_channel_255_fraction':sum(max(p)==255 for p in pixels)/N})
concept=ROOT/'reference/gpt_image_concept.png';ref=concept.read_bytes();cc=chunks(ref)
assert any(t==b'caBX' for t,_,_ in cc) and not any(x in ref for x in PRIVATE)
blend=(ROOT/'A_Place_for_Rain.blend').read_bytes();assert not any(x in blend for x in PRIVATE)
report={'scope':'bounded PNG metadata/pixel and native file path checks, not a general security or physical safety certification',
        'renders':records,'concept':{'file':'reference/gpt_image_concept.png','sha256':sha(ref),
         'c2pa_sha256':sha(b''.join(b for t,b,_ in cc if t==b'caBX')),'c2pa_preserved':True},
        'blend_has_no_private_path_bytes':True}
(ROOT/'bundle_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
