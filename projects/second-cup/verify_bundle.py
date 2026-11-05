"""Verify the frozen public bundle without Blender.

Default verification uses Python's standard library only. Publication helpers
--sanitize and --freeze are explicit; sanitizing additionally uses Pillow to
prove that removing renderer-only text did not change decoded pixel bytes.
Generated reference PNG metadata and C2PA are never modified.
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PUBLIC=['.gitignore','The_Second_Cup.blend','README.md','build.py','audit.py','verify_bundle.py',
        'checks.json','geometry_audit.json','provenance.json','reference/gpt_image_concept.png',
        'reference/concept_prompt.txt','renders/01_blockout.png','renders/the_second_cup_final.png']

def sha(data): return hashlib.sha256(data).hexdigest()
def chunks(data):
    assert data[:8]==b'\x89PNG\r\n\x1a\n','Not PNG'
    at=8
    while at<len(data):
        size=struct.unpack('>I',data[at:at+4])[0]; kind=data[at+4:at+8]; payload=data[at+8:at+8+size]
        raw=data[at:at+12+size]
        assert len(raw)==size+12
        assert struct.unpack('>I',raw[-4:])[0]==zlib.crc32(kind+payload)&0xffffffff,'PNG CRC mismatch'
        yield kind,payload,raw
        at+=size+12
    assert at==len(data)

def idat(data): return b''.join(p for k,p,r in chunks(data) if k==b'IDAT')
def dimensions(data):
    return struct.unpack('>II',next(p for k,p,r in chunks(data) if k==b'IHDR')[:8])

def sanitize():
    from PIL import Image
    import io
    results=[]
    for relative in ('renders/01_blockout.png','renders/the_second_cup_final.png'):
        path=ROOT/relative; raw=path.read_bytes(); original=ROOT/'work'/('raw_'+path.name)
        if original.exists() and idat(original.read_bytes())==idat(raw): raw=original.read_bytes()
        else: original.write_bytes(raw)
        output=raw[:8]; removed=[]
        for kind,payload,packet in chunks(raw):
            if kind in (b'tEXt',b'zTXt',b'iTXt'):
                keyword=payload.split(b'\0',1)[0].decode('latin1')
                if keyword!='Software':
                    # These are renderer records. Refuse to strip authorship or
                    # copyright silently if a future renderer changes its output.
                    assert keyword in ('File','Date','Time','Frame','Camera','Scene','RenderTime','Memory','Samples','Marker','Hostname',
                       'cycles.ViewLayer.samples','cycles.ViewLayer.total_time','cycles.ViewLayer.render_time','cycles.ViewLayer.synchronization_time'), 'Review unexpected PNG text key: '+keyword
                    removed.append(keyword); continue
            output+=packet
        before=Image.open(io.BytesIO(raw)).convert('RGB'); after=Image.open(io.BytesIO(output)).convert('RGB')
        assert before.size==after.size and before.tobytes()==after.tobytes()
        assert idat(raw)==idat(output)
        path.write_bytes(output)
        results.append({'file':relative,'original_sha256':sha(raw),'public_sha256':sha(output),
                        'removed_renderer_text_keys':removed,'idat_sha256':sha(idat(output)),
                        'decoded_rgb_pixels_sha256':sha(after.tobytes()),
                        'idat_unchanged':True,'decoded_pixels_unchanged':True,'dimensions':list(after.size)})
    ref=(ROOT/'reference/gpt_image_concept.png').read_bytes()
    provenance={'title':'두 잔의 자리 · The Second Cup',
      'generated_concept':{'file':'reference/gpt_image_concept.png','sha256':sha(ref),
        'generator':'Built-in GPT Image tool; exact deployed model version not supplied.',
        'prompt_file':'reference/concept_prompt.txt','prompt_sha256':sha((ROOT/'reference/concept_prompt.txt').read_bytes()),
        'use':'Preserved original conceptual reference; packed byte-identically, never used as a material, environment or compositing image.',
        'original_bytes_and_embedded_provenance_preserved':True,
        'png_chunk_types':[k.decode('ascii') for k,p,r in chunks(ref)]},
      'blender_artwork':{'source':'Original independently authored mesh geometry, procedural materials and light rig in build.py.',
        'downloaded_models_textures_or_hdri':False,'concept_is_not_a_render':True,
        'scene_is_not_an_exact_image_reconstruction':True,
        'fiction':'Fictional rainy-town spouse preparing tea before the passenger returns; no real personal biography.'},
      'render_public_copies':results,
      'privacy':'Only this project’s known renderer text keys were removed. Source/reference provenance was not altered. Private render originals stay in ignored work/.',
      'limitations':'Artistic optical approximations; no manufacturing, safety, mechanical, thermal or fluid validation.'}
    (ROOT/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sanitized':[r['file'] for r in results],'pixels_and_idat_identical':True},ensure_ascii=False))

def freeze():
    entries=[]
    for name in PUBLIC:
        data=(ROOT/name).read_bytes(); entries.append({'path':name,'size_bytes':len(data),'sha256':sha(data)})
    manifest={'format_version':1,'title':'The Second Cup','file_count_excluding_manifest':len(entries),
              'manifest_excludes_itself':True,'files':entries}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Frozen',len(entries),'files plus manifest.json')

def verify():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    assert set(e['path'] for e in manifest['files'])==set(PUBLIC)
    for entry in manifest['files']:
        data=(ROOT/entry['path']).read_bytes()
        assert len(data)==entry['size_bytes'],entry['path']+' size differs'
        assert sha(data)==entry['sha256'],entry['path']+' hash differs'
    report=json.loads((ROOT/'geometry_audit.json').read_text())
    assert report['all_assertions_pass'] and all(report['checks'].values())
    assert report['inspected_file']=='The_Second_Cup.blend'
    assert report['render']['resolution']==[1200,1200] and report['render']['samples']==128
    provenance=json.loads((ROOT/'provenance.json').read_text())
    assert provenance['generated_concept']['sha256']==sha((ROOT/'reference/gpt_image_concept.png').read_bytes())
    for entry in provenance['render_public_copies']:
        data=(ROOT/entry['file']).read_bytes()
        assert sha(data)==entry['public_sha256']
        assert sha(idat(data))==entry['idat_sha256']
        assert list(dimensions(data))==entry['dimensions']
        assert entry['idat_unchanged'] and entry['decoded_pixels_unchanged']
        for kind,payload,packet in chunks(data):
            if kind in (b'tEXt',b'zTXt',b'iTXt'):
                assert payload.split(b'\0',1)[0]==b'Software','Unexpected public PNG text'
    assert dimensions((ROOT/'renders/the_second_cup_final.png').read_bytes())==(1200,1200)
    print(json.dumps({'bundle':'The Second Cup','verified_files':len(manifest['files']),
                      'geometry_audit':'pass','final_pixels':[1200,1200],
                      'renderer_paths_removed':True,'reference_bytes_preserved':True},ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--sanitize',action='store_true'); parser.add_argument('--freeze',action='store_true'); args=parser.parse_args()
    if args.sanitize: sanitize()
    if args.freeze: freeze()
    if not args.sanitize or args.freeze: verify()
