"""Idealized one-interface reference; not a shallow puddle or perception validation."""
import bpy,json,math,sys,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['LL']
case=args[0];repeat=case.endswith('_repeat');key=case.removesuffix('_repeat');assert key in ('LL','HL','LH','HH')
band={'L':.2,'H':1.0}[key[0]];floor={'L':1.0,'H':2.0}[key[1]];seed=271 if repeat else 137
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.seed=seed;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.max_bounces=12;s.cycles.diffuse_bounces=4;s.cycles.glossy_bounces=4;s.cycles.transmission_bounces=8;s.cycles.transparent_max_bounces=8;s.cycles.caustics_reflective=True;s.cycles.caustics_refractive=True
s.render.resolution_x=400;s.render.resolution_y=300;s.render.resolution_percentage=100;s.render.use_stamp=False;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=2;s.view_settings.gamma=1
# Generated direction-only environment mask. Equirectangular image v increases northward.
w=s.world;w.use_nodes=True;n=w.node_tree.nodes;n.clear();l=w.node_tree.links
im=bpy.data.images.new('Generated latitude band mask',width=1024,height=512,float_buffer=True);im.colorspace_settings.name='Non-Color'
a=np.zeros((512,1024,4),dtype=np.float32);a[:,:,3]=1
for j in range(512):
 elev=(j+.5)/512*180-90
 if 22.38<=elev<=28.38:a[j,:,:3]=1
im.pixels.foreach_set(a.ravel());im.pack()
env=n.new('ShaderNodeTexEnvironment');env.image=im;env.interpolation='Closest';v=n.new('ShaderNodeValue');v.name='Band_Radiance';v.outputs[0].default_value=band
mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(env.outputs['Color'],mul.inputs[0]);l.new(v.outputs[0],mul.inputs[1]);add=n.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=.05;l.new(mul.outputs[0],add.inputs[0]);bg=n.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(1,1,1,1);l.new(add.outputs[0],bg.inputs['Strength']);out=n.new('ShaderNodeOutputWorld');l.new(bg.outputs[0],out.inputs[0])
# A single +Z interface. The medium below is an ideal half-space, not a thin slab.
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,0));surface=bpy.context.object;surface.name='Ideal water interface';m=bpy.data.materials.new('Water interface IOR 1.333');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,1,1,1);p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333;p.inputs['Roughness'].default_value=0;p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=0;surface.data.materials.append(m)
# Opaque checker floor is fixed 10 mm below the interface. World lights it too.
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.01));ground=bpy.context.object;ground.name='Opaque grid floor';m=bpy.data.materials.new('Diffuse gray checker');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
geo=n.new('ShaderNodeNewGeometry');checker=n.new('ShaderNodeTexChecker');checker.inputs['Scale'].default_value=5;checker.inputs['Color1'].default_value=(.1,.1,.1,1);checker.inputs['Color2'].default_value=(.2,.2,.2,1);l.new(geo.outputs['Position'],checker.inputs['Vector']);f=n.new('ShaderNodeValue');f.name='Floor_Multiplier';f.outputs[0].default_value=floor;mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';l.new(checker.outputs['Color'],mul.inputs[0]);l.new(f.outputs[0],mul.inputs['Scale']);diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Roughness'].default_value=0;l.new(mul.outputs['Vector'],diff.inputs['Color']);out=n.new('ShaderNodeOutputMaterial');l.new(diff.outputs[0],out.inputs[0]);ground.data.materials.append(m)
bpy.ops.object.camera_add(location=(0,-2.135,1.013));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=50;cam.data.sensor_width=36;s.camera=cam;bpy.context.view_layer.update()
assert all(abs(v.co.z)<1e-10 for v in surface.data.vertices);assert surface.data.polygons[0].normal.z>.999;assert len([o for o in s.objects if o.type=='LIGHT'])==0
view=cam.location.normalized();ci=view.z;ct=math.sqrt(1-(1-ci*ci)/(1.333**2));F=.5*(((ci-1.333*ct)/(ci+1.333*ct))**2+((1.333*ci-ct)/(1.333*ci+ct))**2)
record={'case':case,'band_additive_radiance':band,'world_background_radiance':.05,'band_inside_total_radiance':.05+band,'band_elevation_degrees':[22.38,28.38],'floor_multiplier':floor,'floor_linear_grays':[.1*floor,.2*floor],'floor_cell_m':.2,'water_ior':1.333,'water_roughness':0,'surface_z_m':0,'floor_z_m':-.01,'surface_normal':[0,0,1],'camera_location':list(cam.location),'camera_matrix':[list(v) for v in cam.matrix_world],'lens_mm':50,'sensor_width_mm':36,'resolution':[400,300],'samples':32,'seed':seed,'adaptive_sampling':False,'denoising':False,'bounces':[12,4,4,8,8],'view':['AgX','AgX - Medium High Contrast',2,1],'center_view_elevation_degrees':math.degrees(math.asin(ci)),'center_ideal_fresnel':F,'geometry_hash':hashlib.sha256(json.dumps({o.name:[list(v.co) for v in o.data.vertices] for o in (surface,ground)}).encode()).hexdigest(),'model_limit':'Single water interface with ideal half-space below and opaque floor; not a closed shallow-water volume. World change affects floor illumination too.','environment_mask_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
record['roi_definition_sha256']=hashlib.sha256((R/'records/roi_definition.json').read_bytes()).hexdigest() if (R/'records/roi_definition.json').exists() else None
(R/'records'/f'{case}.json').write_text(json.dumps(record,indent=2)+'\n')
s.render.filepath=str(R/'renders'/f'{case}.png');s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
bpy.ops.wm.save_as_mainfile(filepath=str(R/f'{case}.blend'));bpy.ops.render.render(write_still=True)
# Same render result, scene-linear 32-bit RGB EXR without display transform baked in.
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';bpy.data.images['Render Result'].save_render(str(R/'renders'/f'{case}.exr'),scene=s)
# Read EXR back as floats to retain its exact scene-linear values for transparent ROI arithmetic.
exr=bpy.data.images.load(str(R/'renders'/f'{case}.exr'),check_existing=False);arr=np.empty(400*300*4,dtype=np.float32);exr.pixels.foreach_get(arr);arr=arr.reshape((300,400,4))[::-1,:,:3].copy();assert np.isfinite(arr).all();np.save(R/'renders'/f'{case}_linear.npy',arr)
print('COMPLETED',case,arr.min(),arr.max(),flush=True)
