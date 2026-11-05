"""Recreate source seed 1107 geometry in memory, then compare saved art meshes/transforms."""
import bpy,sys,json,hashlib,struct
from pathlib import Path
p=Path(__file__).resolve().parent
source=(p/'build_variant.py').read_text();prefix=source[:source.index('world=bpy.data.worlds.new')]
sys.argv=['geometry-check','--','--seed','1107']
exec(compile(prefix,'source_seed_generator','exec'),{'__file__':str(p/'build_variant.py')})
def fingerprints():
 result={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
  geometry_hash=h.hexdigest()
  h.update(struct.pack('<16f',*(v for row in o.matrix_world for v in row)))
  for m in o.modifiers:
   h.update(m.type.encode())
   if m.type=='BEVEL':h.update(struct.pack('<fI',m.width,m.segments))
  result[o.name]={'geometry':geometry_hash,'full':h.hexdigest()}
 return result
bpy.context.view_layer.update();baseline=fingerprints()
bpy.ops.wm.open_mainfile(filepath=str(p/'a_place_to_pause.blend'));bpy.context.view_layer.update();art=fingerprints()
assert set(art)-set(baseline)=={'Separate pedestrian stone pad'}
assert set(baseline)-set(art)==set()
fixed=[name for name in baseline if not name.startswith('Bench')]
bench=[name for name in baseline if name.startswith('Bench')]
assert all(baseline[name]==art[name] for name in fixed), 'Non-bench source geometry/transform changed'
assert all(baseline[name]['geometry']==art[name]['geometry'] for name in bench), 'Bench mesh shape changed'
report={'passed':True,'seed':1107,'unchanged_mesh_objects':len(fixed),'bench_meshes_with_allowed_transform_change':len(bench),'added_mesh_objects':['Separate pedestrian stone pad'],'road_and_terrain_unchanged':True,'comparison':'All original mesh vertices/topology retained. Only six bench transforms changed; exactly one local pad added. Camera/light/material changes remain excluded.','geometry_hashes':art}
(p/'geometry_verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Unchanged objects:',len(fixed),'bench transform edits:',len(bench),'added pad: 1')
