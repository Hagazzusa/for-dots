from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parent;m=json.loads((R/'ARTIFACT_MANIFEST.json').read_text())
for f in m['files']:
 p=R/f['path'];assert p.is_file() and len(p.read_bytes())==f['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
 if p.suffix=='.png':
  b=p.read_bytes();i=8
  while i<len(b):
   n=struct.unpack('>I',b[i:i+4])[0];assert b[i+4:i+8] not in (b'tEXt',b'iTXt',b'zTXt');i+=n+12
n=json.loads((R/'native_validation.json').read_text());assert n['native_reopened'] and n['finite_evaluated_vertices'] and n['zero_area_faces']==0 and not n['external_file_references'];assert not any(n['private_absolute_path_token_counts'].values())
print(json.dumps({'verified_files':len(m['files']),'no_PNG_text_chunks':True,'native_checks_recorded':True,'manifest_sha256':hashlib.sha256((R/'ARTIFACT_MANIFEST.json').read_bytes()).hexdigest()},indent=2))
