"""Verify the final file and collect reproducible checks without changing the scene."""
from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).resolve().parent
f=P/'One-Body-Two-Shadows.png'
with Image.open(f) as im:
 im.verify()
with Image.open(f) as im:
 assert im.size==(1600,1200)
 assert im.mode in ('RGB','RGBA')
 if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
 image_info={'width':im.width,'height':im.height,'mode':im.mode,'opaque':True}
g=json.loads((P/'geometry-qa.json').read_text());r=json.loads((P/'readback-qa.json').read_text());p=json.loads((P/'projection-qa.json').read_text())
assert g['mode']=='final' and g['form']=='hollow'
assert g['connected_components']==1 and g['nonmanifold_edges']==0
assert r['evaluated_nonmanifold_edges']==0 and r['evaluated_signed_volume']>0
assert all(v['intersection_over_union']>.996 for v in p.values())
assert p['house']['enclosed_holes']==1 and p['tree']['enclosed_holes']==0
regions=json.loads((P/'region-qa.json').read_text());assert regions['comparisons']==17 and regions['maximum_mean_absolute_difference']<.5
report={'region_overlap_maximum_mean_difference_8bit':regions['maximum_mean_absolute_difference'],'title':'그림자가 모르는 것','image':image_info,'source_connected_components':1,'evaluated_nonmanifold_edges':0,'uniform_density_centroid_within_base_extents':r['centroid_projection_within_base_extents'],'silhouette_iou':{k:v['intersection_over_union'] for k,v in p.items()},'checks_scope':'Geometry read-back and sampled orthographic silhouettes; wall-shadow appearance reviewed visually. No physical fabrication or material simulation.'}
(P/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
files=['One-Body-Two-Shadows.png','One-Body-Two-Shadows.blend','build.py','render.py','render_region.py','assemble_regions.py','check_region_overlap.py','region-qa.json','check_mesh_and_masks.py','compare_profiles.py','verify_delivery.py','README.md','description.txt','geometry-qa.json','readback-qa.json','projection-qa.json','qa.json']
manifest={name:{'bytes':(P/name).stat().st_size,'sha256':hashlib.sha256((P/name).read_bytes()).hexdigest()} for name in files}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
