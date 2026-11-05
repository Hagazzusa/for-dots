"""Reads images and writes measurements/comparison sheets; no retouching."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;E=R
cases={'dish':{'baseline':'baseline/dish.png','crop':[150,190,650,540],'patches':{'water_center':[330,350,470,420],'water_edge_left':[210,350,240,420],'ceramic_rim':[330,225,470,245]},'labels':['Baseline: flat top + moved light','Test: boundary fitted inward']},'puddle':{'baseline':'baseline/puddle.png','crop':[65,120,575,325],'patches':{'water_dark_left':[135,190,180,230],'water_center_reflection':[245,190,325,225],'ground_front':[100,330,190,365]},'labels':['Baseline: world strength 0.1','Test: world strength 0.4']}}
report={}
for name,c in cases.items():
 old=Image.open(E/c['baseline']).convert('RGB');new=Image.open(R/name/'comparison.png').convert('RGB');assert old.size==new.size
 a=np.asarray(old,dtype=float);b=np.asarray(new,dtype=float);weights=np.array([.2126,.7152,.0722]);pa=a@weights;pb=b@weights
 patches={}
 for key,(x0,y0,x1,y1) in c['patches'].items():
  aa=pa[y0:y1,x0:x1];bb=pb[y0:y1,x0:x1];delta=bb-aa
  patches[key]={'bounds_px':[x0,y0,x1,y1],'baseline_mean_display_luma':float(aa.mean()),'test_mean_display_luma':float(bb.mean()),'baseline_median':float(np.median(aa)),'test_median':float(np.median(bb)),'mean_difference':float(delta.mean()),'mean_absolute_difference':float(np.abs(delta).mean()),'pixel_difference_std':float(delta.std())}
 box=c['crop'];oa=old.crop(box);nb=new.crop(box);sheet=Image.new('RGB',(oa.width*2+12,oa.height+35),(241,241,237));d=ImageDraw.Draw(sheet);d.text((8,10),c['labels'][0],fill=(20,20,20));d.text((oa.width+20,10),c['labels'][1],fill=(20,20,20));sheet.paste(oa,(0,35));sheet.paste(nb,(oa.width+12,35));sheet.save(R/name/'same_crop_comparison.png')
 record=json.loads((R/name/'test_validation.json').read_text());source=E/record['original_path'];unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==record['original_sha256'];assert unchanged
 report[name]={'baseline_image':c['baseline'],'comparison_image':name+'/comparison.png','crop_box_px':box,'original_blend_unchanged':unchanged,'baseline_image_sha256':hashlib.sha256((E/c['baseline']).read_bytes()).hexdigest(),'test_image_sha256':hashlib.sha256((R/name/'comparison.png').read_bytes()).hexdigest(),'patches':patches}
report['measurement_limits']='Display-encoded 8-bit luma statistics in fixed hand-selected patches; not linear radiometry, reflection contributions, a perceptual user study or Monte Carlo confidence intervals. Same seed does not eliminate sampling differences when scene geometry or illumination changes. No additional noise-estimation renders were made.'
(R/'comparison_metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
