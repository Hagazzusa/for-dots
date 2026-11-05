"""Compare saved rendered silhouettes with independently sampled target equations."""
from pathlib import Path
import numpy as np,json
from scipy import ndimage
from PIL import Image
P=Path(__file__).resolve().parent;cal=json.loads((P/'readback-qa.json').read_text());params=json.loads((P/'geometry-qa.json').read_text())['profiles'];results={}
for name,c in cal['mask_cameras'].items():
 n=c['resolution'];u=(np.arange(n)+.5)/n*c['extent']-c['extent']/2;z=c['center_z']+c['extent']/2-(np.arange(n)+.5)/n*c['extent'];uu,zz=np.meshgrid(u*c['horizontal_polarity'],z)
 if name=='house':
  a=params['house'];inside=(np.abs(uu)<=a['half_width'])&(zz>=0)&(zz<=a['roof_top']-(a['roof_top']-a['wall_top'])*np.abs(uu)/a['half_width'])
  cx=a['door_center'];r=a['door_radius'];cz=a['door_spring_height'];door=((np.abs(uu-cx)<=r)&(zz<=cz))|((uu-cx)**2+(zz-cz)**2<=r*r)
  x0,x1,z0,z1=a['window'];window=(uu>=x0)&(uu<=x1)&(zz>=z0)&(zz<=z1);expected=inside&~door&~window
 else:
  a=params['tree'];expected=(np.abs(uu)<=a['trunk_half_width'])&(zz>=0)&(zz<=a['trunk_top'])
  for cy,cz,ry,rz in a['ellipses']:expected|=((uu-cy)/ry)**2+((zz-cz)/rz)**2<=1
 actual=np.asarray(Image.open(P/'tmp'/f'{name}-mask.png').convert('L'))>=128
 intersection=np.count_nonzero(actual&expected);union=np.count_nonzero(actual|expected);iou=intersection/union
 _,components=ndimage.label(actual);holes=ndimage.binary_fill_holes(actual)&~actual;_,hole_count=ndimage.label(holes)
 assert iou>.985,(name,iou);assert components==1,(name,components);assert hole_count==(1 if name=='house' else 0),(name,hole_count)
 results[name]={'intersection_over_union':iou,'rendered_pixels':int(actual.sum()),'target_pixels':int(expected.sum()),'disagreeing_pixels':int(np.count_nonzero(actual^expected)),'connected_components':components,'enclosed_holes':hole_count}
npth=P/'projection-qa.json';npth.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
