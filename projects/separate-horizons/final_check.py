"""Validate delivered PNG bytes and collect the saved geometry checks."""
from pathlib import Path
import json,hashlib,statistics
from PIL import Image
P=Path(__file__).resolve().parent
f=P/'Separate-Horizons.png';im=Image.open(f);im.verify();im=Image.open(f);assert im.size==(1600,1200)
assert im.getchannel('A').getextrema()==(255,255)
q=json.loads((P/'readback-qa.json').read_text());assert q['render']=={'width':1600,'height':1200,'samples':1024,'denoising':False}
assert all(v==0 for v in q['water_vessel_overlap'].values());assert q['vessel_pair_overlap']==0
rgb=im.convert('RGB');small=rgb.resize((80,60));channels=list(zip(*list(small.get_flattened_data())));deviations=[statistics.pstdev(c) for c in channels];assert min(deviations)>10
raw=f.read_bytes();at=8;kinds=[]
while at<len(raw):
 size=int.from_bytes(raw[at:at+4],'big');kinds.append(raw[at+4:at+8].decode());at+=size+12
assert not set(kinds)&{'tEXt','zTXt','iTXt','eXIf'}
report={'title':'각자의 수평','dimensions':list(im.size),'mode':im.mode,'sha256':hashlib.sha256(raw).hexdigest(),'nonblank_rgb_std':deviations,'png_decodes':True,'fully_opaque':True,'text_metadata_removed':True,'water_surface_height_difference':q['surface_height_range'],'no_water_vessel_triangle_intersections':True,'no_vessel_pair_triangle_intersections':True,'closed_positive_volume_meshes':len(q['meshes']),'frame_margin_fraction':q['frame_min_margin'],'render_samples_max':1024,'denoising':False,'visual_review':'Pending inspection of the final image.','limits':['Static geometry and render validated; no fluid dynamics or mechanical load simulation.','Small boundary clearance keeps water meshes clear of beveled ceramic interiors.']}
(P/'final-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
