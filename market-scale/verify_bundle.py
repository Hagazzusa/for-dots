from pathlib import Path
import hashlib,json,struct,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;m=json.loads((R/'ARTIFACT_MANIFEST.json').read_text())
for f in m['files']:
 p=R/f['path'];b=p.read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
 if p.suffix=='.png':
  i=8
  while i<len(b):
   n=struct.unpack('>I',b[i:i+4])[0];assert b[i+4:i+8] not in (b'tEXt',b'iTXt',b'zTXt');i+=n+12
root=ET.parse(R/'market_scale.svg').getroot();assert not any(n.tag.rsplit('}',1)[-1] in ('image','script','foreignObject','text') for n in root.iter())
print(json.dumps({'verified_files':len(m['files']),'PNG_text_chunks':0,'SVG_XML_reopened':True,'manifest_sha256':hashlib.sha256((R/'ARTIFACT_MANIFEST.json').read_bytes()).hexdigest()},indent=2))
