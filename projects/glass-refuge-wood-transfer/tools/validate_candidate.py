"""Verify the explicit 512 GLB against the 1024 proof without Blender/Godot."""
import struct,json,hashlib,io
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(path):
 b=path.read_bytes();assert b[:4]==b'glTF';n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);pos=20+n;size=struct.unpack_from('<I',b,pos)[0];return d,b[pos+8:pos+8+size]
def view(d,b,i):
 v=d['bufferViews'][i];o=v.get('byteOffset',0);return b[o:o+v['byteLength']]
a,ab=read(ROOT/'assets/refuge_512.glb');b,bb=read(ROOT/'assets/refuge.glb')
assert a['accessors']==b['accessors'] and a['meshes']==b['meshes'] and a['nodes']==b['nodes']
for acc in a['accessors']:assert view(a,ab,acc['bufferView'])==view(b,bb,acc['bufferView'])
assert len(a['images'])==len(a['textures'])==1
im=Image.open(io.BytesIO(view(a,ab,a['images'][0]['bufferView']))).convert('RGB');atlas=Image.open(ROOT/'assets/wood_albedo_512.png').convert('RGB');assert im.size==(512,512) and im.tobytes()==atlas.tobytes()
tris=sum(a['accessors'][pr['indices']]['count']//3 for m in a['meshes'] for pr in m['primitives']);surfaces=sum(len(m['primitives']) for m in a['meshes']);assert (tris,surfaces)==(78388,35)
r={'pass':True,'candidate':'assets/refuge_512.glb','sha256':hashlib.sha256((ROOT/'assets/refuge_512.glb').read_bytes()).hexdigest(),'bytes':(ROOT/'assets/refuge_512.glb').stat().st_size,'images':1,'image_size':list(im.size),'embedded_pixels_match_512':True,'geometry_indices_uv_normals_nodes_identical_to_1024':True,'triangles':tris,'surfaces':surfaces,'mesh_nodes':sum('mesh' in n for n in a['nodes'])}
(ROOT/'qa/candidate_512_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
