"""Verify the frozen public file set without launching Blender.

Run: python3 verify_bundle.py
This checks bytes and recorded assertions, not artistic quality or engineering safety.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'manifest.json').read_text())
failures=[]
for item in manifest['files']:
    relative=Path(item['path'])
    if relative.is_absolute() or '..' in relative.parts:
        failures.append('Unsafe manifest path: '+item['path']);continue
    path=ROOT/relative
    if not path.is_file():
        failures.append('Missing file: '+item['path']);continue
    data=path.read_bytes()
    if len(data)!=item['bytes']:failures.append('Size mismatch: '+item['path'])
    if hashlib.sha256(data).hexdigest()!=item['sha256']:failures.append('Hash mismatch: '+item['path'])
final=ROOT/'renders/mended_corner_final.png'
if final.is_file():
    data=final.read_bytes()
    if data[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',data[16:24])!=(1200,800):
        failures.append('Final render is not the expected 1200 × 800 PNG')
audit=json.loads((ROOT/'geometry_audit.json').read_text())
if not audit['all_assertions_pass']:failures.append('Recorded Blender audit failed')
if audit['inspected_file']!='Mended_Corner.blend':failures.append('Audit did not inspect the final scene')
print(json.dumps({'files_checked':len(manifest['files']),'passed':not failures,'failures':failures},ensure_ascii=False,indent=2))
raise SystemExit(1 if failures else 0)
