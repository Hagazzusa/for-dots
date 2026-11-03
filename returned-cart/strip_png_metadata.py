"""Strip PNG text chunks only; preserve original bytes privately and verify pixels."""
from pathlib import Path
import struct,hashlib,json
from PIL import Image
R=Path(__file__).resolve().parent

def chunks(data):
 i=8;out=[]
 while i<len(data):
  n=struct.unpack('>I',data[i:i+4])[0];out.append((data[i+4:i+8],data[i:i+n+12]));i+=n+12
 return out
reports=[]
for source,target,backup in [('renders/returned_cart_final.png','renders/returned_cart_final.png','private_work/final_render_original.png'),('returned_cart_draft.png','renders/draft.png','private_work/draft_render_original.png')]:
 p=R/source;b=R/backup;b.parent.mkdir(exist_ok=True)
 if not b.exists():b.write_bytes(p.read_bytes())
 original=b.read_bytes();cs=chunks(original);clean=original[:8]+b''.join(blob for kind,blob in cs if kind not in (b'tEXt',b'iTXt',b'zTXt'));out=R/target;out.write_bytes(clean)
 assert [x for t,x in cs if t==b'IDAT']==[x for t,x in chunks(clean) if t==b'IDAT']
 assert Image.open(b).tobytes()==Image.open(out).tobytes()
 reports.append({'file':target,'removed_text_chunks':sum(t in (b'tEXt',b'iTXt',b'zTXt') for t,x in cs),'identical_IDAT':True,'identical_decoded_pixels':True,'original_sha256':hashlib.sha256(original).hexdigest(),'public_sha256':hashlib.sha256(clean).hexdigest()})
(R/'metadata_validation.json').write_text(json.dumps({'pngs':reports,'native':'See native_validation.json; binary tokens and external references inspected after reopen.'},indent=2)+'\n')
