"""Metrics from exact EXR-readback arrays; labelled unretouched display comparisons."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,struct
R=Path(__file__).resolve().parent;roi_raw=(R/'records/roi_definition.json').read_bytes();rois=json.loads(roi_raw)['rois'];sha=hashlib.sha256(roi_raw).hexdigest();cases=['LL','HL','LH','HH','LL_repeat','HH_repeat'];results={}
fixed=['world_background_radiance','band_elevation_degrees','floor_cell_m','water_ior','water_roughness','surface_z_m','floor_z_m','surface_normal','camera_location','camera_matrix','lens_mm','sensor_width_mm','resolution','samples','adaptive_sampling','denoising','bounces','view','geometry_hash','environment_mask_sha256']
base=json.loads((R/'records/LL.json').read_text())
def exr_channels(path):
 b=path.read_bytes();assert struct.unpack('<I',b[:4])[0]==20000630;i=8;attrs={}
 def zstr(pos):
  end=b.index(0,pos);return b[pos:end].decode(),end+1
 while b[i]:
  name,i=zstr(i);typ,i=zstr(i);size=struct.unpack('<I',b[i:i+4])[0];i+=4;attrs[name]=(typ,b[i:i+size]);i+=size
 data=attrs['channels'][1];i=0;channels={}
 while data[i]:
  end=data.index(0,i);name=data[i:end].decode();i=end+1;ptype=struct.unpack('<I',data[i:i+4])[0];i+=16;channels[name]=ptype
 return channels
for case in cases:
 rec=json.loads((R/'records'/f'{case}.json').read_text());assert rec['roi_definition_sha256']==sha
 assert all(rec[k]==base[k] for k in fixed),(case,'fixed setting mismatch')
 a=np.load(R/'renders'/f'{case}_linear.npy');Y=a@np.array([.2126,.7152,.0722]);assert a.shape==(300,400,3) and np.isfinite(a).all()
 channels=exr_channels(R/'renders'/f'{case}.exr');assert set(channels)=={'R','G','B'} and all(x==2 for x in channels.values())
 stats={}
 for name,rr in rois.items():
  x0,y0,x1,y1=rr['bounds_px'];values=Y[y0:y1,x0:x1];stats[name]={'mean_linear_luma':float(values.mean()),'spatial_std':float(values.std()),'pixels':int(values.size)}
 png=np.asarray(Image.open(R/'renders'/f'{case}.png').convert('RGB'));inside=stats['band_inside']['mean_linear_luma'];outside=stats['band_outside']['mean_linear_luma'];bright=stats['grid_bright']['mean_linear_luma'];dark=stats['grid_dark']['mean_linear_luma']
 results[case]={'roi':stats,'band_inside_minus_outside':inside-outside,'grid_bright_minus_dark':bright-dark,'grid_normalized_contrast':(bright-dark)/(bright+dark),'linear_RGB_range':[float(a.min()),float(a.max())],'PNG_channel_max':int(png.max()),'PNG_pixels_with_any_channel_254plus':int(np.any(png>=254,axis=2).sum()),'EXR_channels_pixel_type':channels,'EXR_sha256':hashlib.sha256((R/'renders'/f'{case}.exr').read_bytes()).hexdigest()}
effects={}
for roi in rois:
 v={c:results[c]['roi'][roi]['mean_linear_luma'] for c in cases}
 effects[roi]={'band_change_floor_low':v['HL']-v['LL'],'band_change_floor_high':v['HH']-v['LH'],'floor_change_band_low':v['LH']-v['LL'],'floor_change_band_high':v['HH']-v['HL'],'two_factor_interaction':v['HH']-v['HL']-v['LH']+v['LL'],'LL_other_seed_delta':v['LL_repeat']-v['LL'],'HH_other_seed_delta':v['HH_repeat']-v['HH']}
report={'fixed_ROI_sha256':sha,'fixed_settings_match_all_cases':True,'linear_luma_weights':[.2126,.7152,.0722],'values_from':'32-bit linear RGB OpenEXR read through Blender Linear Rec.709, top-left array stored in *_linear.npy','cases':results,'effects':effects,'limits':'ROI spatial std is not Monte Carlo standard error. Only two seeds at two extremes; no confidence intervals or significance claim. World amplitude changes floor illumination too; ROI effects are not isolated reflection/transmission contributions.'}
(R/'records/analysis.json').write_text(json.dumps(report,indent=2)+'\n')
def sheet(names,title,path):
 out=Image.new('RGB',(812,670),(235,235,231));d=ImageDraw.Draw(out);d.text((10,8),title,fill='black')
 for idx,(case,label) in enumerate(names):
  x=(idx%2)*412;y=28+(idx//2)*322;d.text((x+7,y),label,fill='black');out.paste(Image.open(R/'renders'/f'{case}.png').convert('RGB'),(x,y+18))
 out.save(R/path)
sheet([('LL','Band +0.2 / Floor x1'),('HL','Band +1.0 / Floor x1'),('LH','Band +0.2 / Floor x2'),('HH','Band +1.0 / Floor x2')],'2 x 2 ideal-interface reference; identical AgX +2 display','matrix.png')
sheet([('LL','LL seed 137'),('LL_repeat','LL seed 271'),('HH','HH seed 137'),('HH_repeat','HH seed 271')],'Extremes only: one additional seed each','seed_comparison.png')
im=Image.open(R/'renders/LL.png').convert('RGB');d=ImageDraw.Draw(im);colors=['#ff7060','#60d0ff','#ffff60','#bfa0ff']
for (name,r),color in zip(rois.items(),colors):d.rectangle(r['bounds_px'],outline=color,width=1);d.text((r['bounds_px'][0],r['bounds_px'][1]-10),name,fill=color)
im.save(R/'roi_layout.png')
print(json.dumps({'effects':effects,'contrast':{c:{'band':results[c]['band_inside_minus_outside'],'grid':results[c]['grid_bright_minus_dark'],'grid_normalized':results[c]['grid_normalized_contrast']} for c in cases}},indent=2))
