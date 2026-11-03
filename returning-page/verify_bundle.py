"""Verify the frozen public allowlist and the CAD mesh's closed edge topology."""
from pathlib import Path
from collections import Counter
import json, hashlib, math
R=Path(__file__).resolve().parent
m=json.loads((R/'cad/bookmark_mesh.json').read_text()); vs=m['vertices']; fs=m['faces']
edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in fs for i in range(3))
assert all(n==2 for n in edges.values()),'Mesh is not closed edge-manifold'
assert all(math.isfinite(x) for v in vs for x in v)
volume=0
for f in fs:
 a,b,c=[vs[i] for i in f]
 volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
cad=json.loads((R/'cad/validation.json').read_text()); rel=abs(abs(volume)-cad['volume_mm3'])/cad['volume_mm3']; assert rel<.001
manifest=json.loads((R/'ARTIFACT_MANIFEST.json').read_text())
for rec in manifest['files']:
 p=R/rec['path']; assert p.is_file() and p.stat().st_size==rec['bytes']; assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],p
print(json.dumps({'frozen_files_verified':len(manifest['files']),'finite_vertices':True,'closed_edge_manifold':True,'tessellation_volume_relative_error':rel,'manifest_sha256':hashlib.sha256((R/'ARTIFACT_MANIFEST.json').read_bytes()).hexdigest()},indent=2))
