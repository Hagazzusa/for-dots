"""Standard-library verification of the immutable runtime asset sub-bundle.

python3 verify_asset.py          # verify only
python3 verify_asset.py --freeze # explicitly update the asset-only manifest
Viewer scenes, scripts, font and runtime QA belong to the separate viewer bundle.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FILES=['assets/second_cup_tableau.glb','export_from_blender.py','export_audit.json',
       'ASSET_README.md','asset_provenance.json','verify_asset.py']
def sha(data):return hashlib.sha256(data).hexdigest()
def glb_document(data):
    magic,version,length=struct.unpack_from('<4sII',data,0)
    assert magic==b'glTF' and version==2 and length==len(data)
    at=12;document=None
    while at<len(data):
        size,kind=struct.unpack_from('<II',data,at)
        if kind==0x4e4f534a:document=json.loads(data[at+8:at+8+size])
        at+=8+size
    assert document and at==len(data)
    return document

def freeze():
    records=[]
    for name in FILES:
        data=(ROOT/name).read_bytes();records.append({'path':name,'size_bytes':len(data),'sha256':sha(data)})
    record={'schema_version':1,'scope':'Second Cup runtime GLB derivative and its export tools only; excludes viewer code and native QA.',
            'manifest_excludes_itself':True,'files':records}
    (ROOT/'asset_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')

def verify():
    manifest=json.loads((ROOT/'asset_manifest.json').read_text())
    assert set(e['path'] for e in manifest['files'])==set(FILES)
    for e in manifest['files']:
        data=(ROOT/e['path']).read_bytes()
        assert len(data)==e['size_bytes'] and sha(data)==e['sha256'],e['path']
        private_prefixes=(b'/' + b'workspace' + b'/scratch/', b'/' + b'home' + b'/agent')
        assert not any(prefix in data for prefix in private_prefixes)
    report=json.loads((ROOT/'export_audit.json').read_text())
    provenance=json.loads((ROOT/'asset_provenance.json').read_text())
    assert report['all_assertions_pass'] and all(report['checks'].values())
    data=(ROOT/'assets/second_cup_tableau.glb').read_bytes();doc=glb_document(data)
    assert sha(data)==report['output_sha256']==provenance['derivative']['sha256']
    assert report['producer_blend_sha256']==provenance['source']['sha256']
    assert len(doc['meshes'])==19 and len(doc['materials'])==6
    assert not doc.get('images') and not doc.get('textures') and not doc.get('animations') and not doc.get('cameras')
    assert all('uri' not in b for b in doc['buffers'])
    assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' and not m.get('extensions') for m in doc['materials'])
    triangle_count=0
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            assert p.get('mode',4)==4
            count=doc['accessors'][p['indices']]['count'];assert count%3==0;triangle_count+=count//3
            assert 'NORMAL' in p['attributes'] and 0<=p['material']<6
    assert triangle_count==62072==report['triangles']
    print(json.dumps({'asset_bundle':'pass','files_excluding_manifest':len(FILES),
      'glb_bytes':len(data),'meshes':19,'triangles':triangle_count,'materials':6,
      'producer_source_hash':report['producer_blend_sha256'],'glb_sha256':sha(data)},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    verify()
