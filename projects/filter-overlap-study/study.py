"""Controlled RGB thin-filter study; Blender 4.3+, two CPU threads."""
import bpy, json
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=False; s.cycles.seed=17
s.cycles.max_bounces=8; s.cycles.diffuse_bounces=4; s.cycles.transparent_max_bounces=12
s.render.threads_mode='FIXED'; s.render.threads=2; s.render.resolution_x=s.render.resolution_y=256; s.render.resolution_percentage=100
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
s.view_settings.view_transform='Standard'; s.view_settings.look='None'; s.view_settings.exposure=0; s.view_settings.gamma=1
s.render.image_settings.file_format='OPEN_EXR'; s.render.image_settings.color_depth='32'; s.render.image_settings.color_mode='RGBA'
# Only floor, single white area light and two filters: no environmental spill or emitters.
bpy.ops.mesh.primitive_plane_add(size=6); floor=bpy.context.object; floor.name='Identical matte measurement plane'
m=bpy.data.materials.new('Neutral diffuse 0.8'); m.use_nodes=True; n=m.node_tree.nodes; n.clear(); bs=n.new('ShaderNodeBsdfDiffuse'); bs.inputs['Color'].default_value=(.8,.8,.8,1); out=n.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(bs.outputs[0],out.inputs[0]); floor.data.materials.append(m)
bpy.ops.object.light_add(type='AREA',location=(0,0,4)); light=bpy.context.object; light.name='Fixed white reference'; light.data.energy=140; light.data.size=.15; light.data.color=(1,1,1)
bpy.ops.object.camera_add(location=(0,0,5)); camera=bpy.context.object; camera.name='Top-down measurement camera'; camera.data.type='ORTHO'; camera.data.ortho_scale=3.5; s.camera=camera
C=np.array([.2,.85,.9]); Y=np.array([.95,.85,.2])
def filter_material(name,color,mix):
 m=bpy.data.materials.new(name); m.use_nodes=True; n=m.node_tree.nodes; n.clear(); l=m.node_tree.links
 t=n.new('ShaderNodeBsdfTransparent'); t.inputs['Color'].default_value=(*color,1); d=n.new('ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value=(*color,1)
 mixnode=n.new('ShaderNodeMixShader'); mixnode.inputs[0].default_value=mix; l.new(t.outputs[0],mixnode.inputs[1]); l.new(d.outputs[0],mixnode.inputs[2]); out=n.new('ShaderNodeOutputMaterial'); l.new(mixnode.outputs[0],out.inputs[0]); return m
panels=[]
for name,z,size,color in [('Cyan',1,1.8,C),('Yellow',1.5,1.5,Y)]:
 bpy.ops.mesh.primitive_plane_add(size=size,location=(0,0,z)); ob=bpy.context.object; ob.name=name+' filter (camera hidden, shadow active)'; ob.visible_camera=False; ob.data.materials.append(filter_material(name+' pure',color,0)); panels.append(ob)
variants=[('00_control',False,False,False,np.ones(3)),('01_cyan',True,False,False,C),('02_yellow',False,True,False,Y),('03_overlap_pure',True,True,False,C*Y),('04_overlap_gallery',True,True,True,C*Y*.88**2),('05_gallery_direct_only',True,True,True,C*Y*.88**2)]
rows=[]; baseline=None
for name,cyan,yellow,hybrid,expected in variants:
 s.cycles.diffuse_bounces=0 if name=='05_gallery_direct_only' else 4
 for ob,visible,color in zip(panels,[cyan,yellow],[C,Y]):
  ob.hide_render=not visible; ob.data.materials.clear(); ob.data.materials.append(filter_material(ob.name+name,color,.12 if hybrid else 0))
 s.render.filepath=str(ROOT/(name+'.exr')); bpy.ops.render.render(write_still=True)
 # EXR is 32-bit scene-linear, not display PNG/AgX values. Load as float buffer.
 im=bpy.data.images.load(s.render.filepath,check_existing=False); assert im.is_float; pixels=np.array(im.pixels[:],dtype=np.float64).reshape(256,256,4)
 patch=pixels[112:144,112:144,:3]; mean=patch.mean(axis=(0,1)); assert np.isfinite(patch).all() and (mean>0).all()
 if baseline is None: baseline=mean
 ratio=mean/baseline
 rows.append({'case':name,'linear_patch_mean':mean.tolist(),'normalized_to_control':ratio.tolist(),'direct_path_prediction':expected.tolist(),'max_absolute_prediction_error':float(np.abs(ratio-expected).max()),'loaded_colorspace':im.colorspace_settings.name,'diffuse_bounces':s.cycles.diffuse_bounces})
 # Display preview uses Standard/sRGB at identical exposure; never used for measurement.
 s.render.image_settings.file_format='PNG'; s.render.image_settings.color_depth='8'; bpy.data.images['Render Result'].save_render(str(ROOT/(name+'.png')),scene=s); s.render.image_settings.file_format='OPEN_EXR'; s.render.image_settings.color_depth='32'
 bpy.data.images.remove(im)
report={'blender':bpy.app.version_string,'samples':64,'seed':17,'threads':2,'patch_bounds_xy':[112,144],'exposure':0,'display_transform':'Standard / sRGB; measurement bypasses display transform','cases':rows,'pure_overlap_pass':rows[3]['max_absolute_prediction_error']<.005,'hybrid_caveat':'Prediction includes 0.88 transmission weight per sheet; residual can include diffuse interreflection and Monte Carlo noise.'}
assert report['pure_overlap_pass'],report
(ROOT/'measurements.json').write_text(json.dumps(report,indent=2))
s['study']='RGB non-refractive filters, not spectral materials. Camera visibility off only to isolate the floor; shadow rays interact normally.'; s.render.filepath='//study.exr'; bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Filter-Overlap.blend')); print('STUDY_RESULT',json.dumps(report))
