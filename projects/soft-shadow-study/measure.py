"""Finite-emitter penumbra test; original scene, Blender 4.3+, no external assets."""
import bpy, json, csv
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent; N=384; FIELD=4.; LIGHT_Z=4.; T=.2
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=96; s.cycles.use_denoising=False; s.cycles.seed=23; s.cycles.diffuse_bounces=0; s.cycles.transparent_max_bounces=12
s.render.threads_mode='FIXED'; s.render.threads=2; s.render.resolution_x=s.render.resolution_y=N; s.render.resolution_percentage=100
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
s.view_settings.view_transform='Standard'; s.view_settings.look='None'; s.view_settings.exposure=0; s.view_settings.gamma=1
s.render.image_settings.file_format='OPEN_EXR'; s.render.image_settings.color_depth='32'
def material(name,kind,color):
 m=bpy.data.materials.new(name); m.use_nodes=True; n=m.node_tree.nodes; n.clear(); bs=n.new(kind); bs.inputs['Color'].default_value=(*color,1); out=n.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(bs.outputs[0],out.inputs[0]); return m
bpy.ops.mesh.primitive_plane_add(size=8); floor=bpy.context.object; floor.name='Fixed receiver'; floor.data.materials.append(material('Neutral matte','ShaderNodeBsdfDiffuse',(.8,.8,.8)))
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,.5)); filt=bpy.context.object; filt.name='Thin cyan filter'; filt.scale=(1.2,1.6,1); filt.visible_camera=False; filt.data.materials.append(material('Non-refracting cyan','ShaderNodeBsdfTransparent',(.2,.85,.9)))
bpy.ops.object.light_add(type='AREA',location=(0,0,LIGHT_Z)); light=bpy.context.object; light.name='Finite square emitter'; light.data.energy=140; light.data.shape='SQUARE'
bpy.ops.object.camera_add(location=(0,0,5)); s.camera=bpy.context.object; s.camera.data.type='ORTHO'; s.camera.data.ortho_scale=FIELD
x=(np.arange(N)+.5)*FIELD/N-FIELD/2

def render(name):
 s.render.filepath=str(ROOT/(name+'.exr')); bpy.ops.render.render(write_still=True); im=bpy.data.images.load(s.render.filepath,check_existing=False); assert im.is_float and im.colorspace_settings.name=='Linear Rec.709'; arr=np.array(im.pixels[:],dtype=np.float64).reshape(N,N,4); bpy.data.images.remove(im)
 s.render.image_settings.file_format='PNG'; s.render.image_settings.color_depth='8'; bpy.data.images['Render Result'].save_render(str(ROOT/(name+'.png')),scene=s); s.render.image_settings.file_format='OPEN_EXR'; s.render.image_settings.color_depth='32'; return arr

def crossing(profile,threshold,center,span):
 # Threshold interpolation near the known right edge, not a whole-image first crossing.
 ids=np.where((x>center-span)&(x<center+span))[0]
 for i in ids[:-1]:
  if profile[i]<=threshold and profile[i+1]>=threshold:
   return float(x[i]+(threshold-profile[i])/(profile[i+1]-profile[i])*(x[i+1]-x[i]))
 raise RuntimeError('Missing threshold crossing')
rows=[]; profiles=[]
for width in [.3,.9]:
 light.data.size=width; filt.hide_render=True; control=render(f'control_w{width:.1f}')
 for gap in [.5,1.,1.5]:
  filt.hide_render=False; filt.location.z=gap; name=f'w{width:.1f}_gap{gap:.1f}'; arr=render(name)
  # Normalize each pixel before averaging 16 central scanlines. 0=filtered; 1=unfiltered.
  ratio=arr[N//2-8:N//2+8,:,0]/control[N//2-8:N//2+8,:,0]; profile=((ratio-T)/(1-T)).mean(axis=0)
  center=.6*LIGHT_Z/(LIGHT_Z-gap); full=width*gap/(LIGHT_Z-gap); lo=crossing(profile,.1,center,full/2+.06); hi=crossing(profile,.9,center,full/2+.06)
  rows.append({'case':name,'emitter_width':width,'filter_receiver_gap':gap,'x10':lo,'x90':hi,'measured_10_90_width':hi-lo,'geometric_full_penumbra':full,'uniform_emitter_10_90_approx':.8*full,'width_in_pixels':(hi-lo)/(FIELD/N)})
  profiles.append((name,profile))
with (ROOT/'edge_profiles.csv').open('w') as f:
 writer=csv.writer(f); writer.writerow(['x_scene_units']+[name for name,_ in profiles]); writer.writerows(zip(x,*[p for _,p in profiles]))
checks={'increases_with_gap':all(rows[i]['measured_10_90_width']<rows[i+1]['measured_10_90_width'] for i in [0,1,3,4]),'wider_emitter_is_softer':all(rows[i+3]['measured_10_90_width']>rows[i]['measured_10_90_width'] for i in range(3))}; assert all(checks.values())
report={'blender':bpy.app.version_string,'resolution':N,'samples':96,'threads':2,'world_strength':0,'indirect_diffuse_bounces':0,'measurement_colorspace':'Linear Rec.709','threshold_definition':'u=(Ired/Ired_control-0.2)/0.8; width=x(u=.9)-x(u=.1), average 16 central scanlines','pixel_pitch':FIELD/N,'source_receiver_distance':LIGHT_Z,'checks':checks,'cases':rows}
(ROOT/'measurements.json').write_text(json.dumps(report,indent=2)); s.render.filepath='//measurement.exr'; bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Soft-Shadow-Measurement.blend')); print(json.dumps(report))
