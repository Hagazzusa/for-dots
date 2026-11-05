#!/usr/bin/env python3
"""Read-only, standard-library evidence/file audit. Does not recompute CAD/physics.
python consolidation/validate.py --negative-test [--manifest BACKUP_MANIFEST.json]
"""
import argparse,ast,copy,hashlib,json,math,re,struct,subprocess,sys,zlib,zipfile
from pathlib import Path,PurePosixPath
import xml.etree.ElementTree as ET
import shutil,tempfile
PNG=b'\x89PNG\r\n\x1a\n'
PRIVATE_TOKENS=[('/'+'workspace/').encode(),('/'+'home/agent/').encode()]
def sha(data):return hashlib.sha256(data).hexdigest()
def relcheck(value):
 p=PurePosixPath(value)
 if p.is_absolute() or '..' in p.parts or '\\' in value:raise ValueError('unsafe/nonrelative project path: '+value)
 return p

def png_chunks(data):
 if not data.startswith(PNG):raise ValueError('bad PNG header')
 pos=8;out=[]
 while pos<len(data):
  if pos+12>len(data):raise ValueError('truncated PNG chunk')
  n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];end=pos+12+n
  if end>len(data):raise ValueError('truncated PNG payload')
  payload=data[pos+8:pos+8+n];crc=struct.unpack('>I',data[pos+8+n:end])[0]
  if zlib.crc32(kind+payload)&0xffffffff!=crc:raise ValueError('PNG CRC mismatch')
  out.append((kind,payload,data[pos:end]));pos=end
  if kind==b'IEND':break
 if pos!=len(data) or not out or out[-1][0]!=b'IEND':raise ValueError('bad PNG termination')
 return out

def png_text(kind,payload):
 try:
  if kind==b'zTXt':return zlib.decompress(payload.split(b'\0',1)[1][1:])
  if kind==b'iTXt':
   _,rest=payload.split(b'\0',1);compressed=rest[0];rest=rest[2:];_,rest=rest.split(b'\0',1);_,text=rest.split(b'\0',1)
   return zlib.decompress(text) if compressed else text
 except Exception:raise ValueError('unreadable PNG text metadata')
 return payload

def catalog_paths(catalog):
 if catalog.get('schema_version')!=1:raise ValueError('unsupported catalog schema')
 levels=set(catalog['evidence_levels']);paths=[];ids=set()
 for s in catalog['studies']:
  if s['id'] in ids:raise ValueError('duplicate study id')
  ids.add(s['id']);relcheck(s['directory'])
  if not s['evidence'] or not set(s['evidence'])<=levels:raise ValueError('invalid evidence classification')
  if 'unvalidated_hardware' not in s['evidence']:raise ValueError('missing hardware limitation')
  for name in s['required']+s.get('optional',[]):
   relcheck(name);paths.append(str(PurePosixPath(s['directory'])/name))
 paths+=catalog['consolidation_files']
 for x in paths:relcheck(x)
 if len(paths)!=len(set(paths)):raise ValueError('duplicate catalog file')
 return paths

def finite_tree(obj):
 if isinstance(obj,float) and not math.isfinite(obj):raise ValueError('nonfinite result')
 if isinstance(obj,dict):
  for x in obj.values():finite_tree(x)
 elif isinstance(obj,list):
  for x in obj:finite_tree(x)

def audit(root,manifest=None,negative=False):
 root=Path(root).resolve();errors=[];warnings=[];checks=[];metadata=[];jsons={};cad_counts={}
 def require(ok,msg):
  if not ok:errors.append(msg)
 try:
  cat=json.loads((root/'consolidation/study_catalog.json').read_text());paths=catalog_paths(cat)
 except Exception as e:return {'ok':False,'errors':[str(e)],'warnings':[],'checks':[]}
 for name in paths:
  p=root/name
  if not p.is_file():
   optional={str(PurePosixPath(s['directory'])/n) for s in cat['studies'] for n in s.get('optional',[])}
   if name in optional:warnings.append('Optional generated derivative omitted: '+name)
   else:errors.append('missing '+name)
   continue
  data=p.read_bytes()
  try:
   if p.suffix in ('.py','.md','.json','.svg'):
    text=data.decode('utf-8')
    require(not any(t in data for t in PRIVATE_TOKENS),'private absolute workspace/home path in '+name)
    if p.suffix=='.py':
     ast.parse(text,filename=name)
     if not name.startswith('consolidation/') and ('/usr/lib/freecad/lib' in text or '/usr/bin/python3' in text or '/tmp/rain-clock-mpl' in text):metadata.append({'file':name,'kind':'declared_platform_runtime_path'})
    if p.suffix=='.json':jsons[name]=json.loads(text);finite_tree(jsons[name])
    if p.suffix=='.svg':ET.fromstring(text)
    if p.suffix=='.md' and re.search(r'no (?:external assets, )?(?:uploads|publication)|no[^\n]{0,80}uploads or publication',text,re.I):
     if name in cat['historical_status_notes']:warnings.append('Historical creation/publication wording reconciled by STUDY_INDEX: '+name)
     else:errors.append('Unreconciled publication/local-only statement: '+name)
   elif p.suffix=='.png':
    chunks=png_chunks(data);require(chunks[0][0]==b'IHDR','missing PNG IHDR: '+name)
    w,h=struct.unpack('>II',chunks[0][1][:8]);require(w>0 and h>0,'invalid PNG dimensions: '+name)
    for kind,payload,_ in chunks:
     if kind in (b'tEXt',b'zTXt',b'iTXt',b'eXIf') and any(t in png_text(kind,payload) for t in PRIVATE_TOKENS):metadata.append({'file':name,'kind':'private_png_path_metadata'})
   elif p.suffix=='.FCStd':
    with zipfile.ZipFile(p) as z:
     require(z.testzip() is None,'CAD ZIP CRC failure: '+name);xml=z.read('Document.xml');tree=ET.fromstring(xml)
     for member in z.namelist():
      if member.endswith('.xml'):require(not any(t in z.read(member) for t in PRIVATE_TOKENS),'private CAD XML path: '+name)
     elem=tree.find('Objects');cad_counts[name]=int(elem.attrib['Count']) if elem is not None else None
   elif p.suffix=='.gif':require(data[:6] in (b'GIF87a',b'GIF89a'),'bad GIF header: '+name)
   elif p.suffix=='.mp4':require(b'ftyp' in data[:64] and b'moov' in data and b'mdat' in data,'missing MP4 boxes: '+name)
   checks.append('file:'+name)
  except Exception as e:errors.append(name+': '+str(e))
 # Frozen-result contracts: integrity and mutual consistency, NOT independent scientific validation.
 try:
  d=jsons['verification.json'];require(d['render_verified'] is True and d['preview']['frames']==48 and d['preview']['seconds']==8,'art verification contract')
  d=jsons['mechanism/geometry_checks.json'];require(d['parts']==79 and d['valid_solids'] and d['minimum_full_cycle_shelter_Y_gap_mm']==16,'nominal rim contract');require(len(d['ring_roller_contacts'])==6 and all(x['overlap_mm3']<1e-6 for x in d['ring_roller_contacts']),'nominal contact contract')
  d=jsons['mechanism/sensitivity/results.json'];s=jsons['mechanism/sensitivity/summary.json'];require(len(d['axial_scenarios'])==s['axial_cases']==1920,'axial scenario count');require(len(d['radial_first_order_scenarios'])==s['radial_cases']==5184,'radial scenario count');require(len(d['nonlinear_spot_checks'])==14,'nonlinear scenario count')
  d=jsons['mechanism/cartridge/cartridge_geometry.json'];require(d['parts']==14 and d['valid_solids'],'cartridge contract');require(all(x['stop_overlap_mm3']<1e-6 if abs(x['delta_mm'])<=1 else x['stop_overlap_mm3']>0 for x in d['stop_checks']),'cartridge stop contract')
  d=jsons['mechanism/cartridge/load_path.json'];require(d['unit_test_max_force_or_moment_residual']<1e-12,'load-path residual contract')
  d=jsons['mechanism/cartridge/contact_motion.json'];require(len(d['samples'])==50 and d['summary']['max_contact_residual_mm']<1e-7,'sampled contact contract')
  d=jsons['mechanism/escape/results.json'];s=jsons['mechanism/escape/summary.json'];require(len(d['results'])==2,'escape result count')
  for a,b in zip(d['results'],s['results']):
   require(a['outcome'].startswith('inconclusive'),'escape outcome must remain inconclusive in this checkpoint')
   for key in ['unique_grid_poses_tested','reachable_grid_poses','checked_edge_midpoints']:require(a[key]==b[key],'escape summary mismatch: '+key)
   require(a['reachable_grid_poses']==len(a['reachable_poses']),'escape reachable count')
  d=jsons['mechanism/axle_comparison/geometry_comparison.json'];require(d['parts']==71 and d['exact_support_window_tests']==680 and not d['window_intersections'],'rear axle contract')
  d=jsons['mechanism/front_facade/geometry_comparison.json'];require(d['parts']==71 and d['moving_window_broadphase_pairs']==3536 and d['exact_intersections_evaluated']==17 and not d['window_intersections'],'front facade contract');require(d['dimensions']['rotating_forward_bridge_lengths_mm']==[0,0] and d['dimensions']['bead_to_hub_offsets_mm']==[14,14],'front facade coordinate contract')
  expected={'mechanism/rain_clock_manual.FCStd':79,'mechanism/sensitivity/groove_variants.FCStd':6,'mechanism/cartridge/rear_cartridge_envelope.FCStd':15,'mechanism/escape/escape_search_solids.FCStd':4,'mechanism/axle_comparison/rear_axle_alternative.FCStd':71,'mechanism/front_facade/front_facade_axle.FCStd':71}
  for name,n in expected.items():require(cad_counts.get(name)==n,'CAD document object count: '+name)
  checks.append('frozen-result-contracts-and-CAD-object-counts')
 except Exception as e:errors.append('result schema/contract failure: '+str(e))
 # Verify all source-to-source project dependencies are available in the preserved tree.
 for rel in ['mechanism/rain_clock_manual.FCStd','mechanism/axle_comparison/build_alternative.py','mechanism/front_facade/build_concept.py']:
  require((root/rel).is_file(),'relative build dependency missing: '+rel)
 checks.append('project-tree-relative-dependencies; platform-runtime-paths-disclosed')
 ffprobe=shutil.which('ffprobe')
 if ffprobe:
  try:
   cmd=[ffprobe,'-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate','-show_entries','format=duration','-of','json',str(root/'rain_clock_loop.mp4')]
   v=json.loads(subprocess.check_output(cmd,text=True,timeout=20));st=v['streams'][0];require(st['width']==480 and st['height']==480 and st['nb_frames']=='48' and abs(float(v['format']['duration'])-8)<.01,'video metadata contract');checks.append('ffprobe-video-contract')
  except Exception as e:errors.append('video check: '+str(e))
 else:warnings.append('ffprobe absent: MP4 container boxes checked, duration/frame metadata not rechecked')
 if metadata:
  for m in metadata:
   if m['kind']=='private_png_path_metadata':warnings.append('Backup must sanitize PNG metadata without changing IDAT pixels: '+m['file'])
  if any(m['kind']=='declared_platform_runtime_path' for m in metadata):warnings.append('Historical builders are platform-bound at runtime; project-data paths are relative. See catalog requirements.')
 # Manifest paths are guarded before reading; hashes cover exact staged bytes.
 if manifest:
  try:
   mf=json.loads(Path(manifest).read_text());require(mf['schema_version']==1,'manifest schema')
   for item in mf['files']:
    relcheck(item['path']);p=root/item['path'];require(p.is_file(),'manifest missing '+item['path'])
    if p.is_file():b=p.read_bytes();require(len(b)==item['size_bytes'] and sha(b)==item['sha256'],'manifest hash/size mismatch '+item['path'])
   require(not any(m['kind']=='private_png_path_metadata' for m in metadata),'staged payload still has private PNG metadata');checks.append('backup-manifest-hashes')
  except Exception as e:errors.append('manifest validation: '+str(e))
 neg=[]
 if negative:
  for label,mutate in [('unsupported evidence claim',lambda c:c['studies'][0]['evidence'].append('manufacture_ready')),('path traversal',lambda c:c['studies'][0]['required'].append('../outside.json'))]:
   c=copy.deepcopy(cat);mutate(c)
   try:catalog_paths(c);errors.append('negative test unexpectedly accepted '+label)
   except ValueError:neg.append('rejected '+label)
  if manifest:
   damaged=copy.deepcopy(json.loads(Path(manifest).read_text()));damaged['files'][0]['sha256']='0'*64
   with tempfile.TemporaryDirectory(prefix='rain-clock-negative-') as td:
    bad=Path(td)/'bad_manifest.json';bad.write_text(json.dumps(damaged));test=audit(root,manifest=bad,negative=False)
    if test['ok'] or not any('manifest hash/size mismatch' in x for x in test['errors']):errors.append('negative test unexpectedly accepted corrupted manifest hash')
    else:neg.append('rejected corrupted manifest hash')
  checks.append('intentional-negative-tests')
 return {'schema_version':1,'ok':not errors,'scope':'File/result integrity only; no CAD regeneration, rendering, independent mathematical proof or hardware certification.','errors':errors,'warnings':sorted(set(warnings)),'checks':checks,'metadata_findings':metadata,'negative_tests':neg,'files_checked':len(paths),'cad_document_object_counts':cad_counts}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--manifest',type=Path);ap.add_argument('--negative-test',action='store_true');args=ap.parse_args();r=audit(args.root,args.manifest,args.negative_test);print(json.dumps(r,indent=2));return 0 if r['ok'] else 1
if __name__=='__main__':sys.exit(main())
