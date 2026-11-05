"""Single 1024 albedo transfer proof; no lighting, normal, ORM or original-file save."""
import bpy,json,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];validation=json.loads((ROOT/'qa/wood_uv_validation.json').read_text());assert validation['pass'] and validation['resolution']==512
obj=bpy.data.objects['Oak_Baked_Atlas'];mat=bpy.data.materials['Oak | long grain / warm honey'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
ramp=next(n for n in nodes if n.bl_idname=='ShaderNodeValToRGB');output=next(n for n in nodes if n.bl_idname=='ShaderNodeOutputMaterial')
em=nodes.new('ShaderNodeEmission');links.new(ramp.outputs['Color'],em.inputs['Color']);em.inputs['Strength'].default_value=1
for l in list(output.inputs['Surface'].links):links.remove(l)
links.new(em.outputs[0],output.inputs['Surface'])
img=bpy.data.images.new('Wood albedo | 1024 transfer proof',width=1024,height=1024,alpha=False,float_buffer=False);img.colorspace_settings.name='sRGB'
target=nodes.new('ShaderNodeTexImage');target.image=img;target.label='BAKE TARGET | albedo only';nodes.active=target
for n in nodes:n.select=False
target.select=True
for o in bpy.context.scene.objects:o.hide_render=o!=obj
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
obj.data.uv_layers.active=obj.data.uv_layers['WoodAtlas'];obj.data.uv_layers.active.active_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.bake.margin=8;s.render.bake.margin_type='EXTEND';s.render.bake.use_clear=True
start=time.monotonic();bpy.ops.object.bake(type='EMIT',margin=8,use_clear=True);elapsed=time.monotonic()-start
out=ROOT/'assets/wood_albedo_1024.png';img.filepath_raw=str(out);img.file_format='PNG';img.save()
# Restore a conventional texture-driven material in this derivative only for inspection/export.
p=nodes.get('Principled BSDF')
for l in list(p.inputs['Base Color'].links):links.remove(l)
for l in list(p.inputs['Normal'].links):links.remove(l)
links.new(target.outputs['Color'],p.inputs['Base Color'])
for l in list(output.inputs['Surface'].links):links.remove(l)
links.new(p.outputs['BSDF'],output.inputs['Surface'])
img.pack();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tmp/wood_1024_proof.blend'),compress=True)
report={'type':'1024 albedo-only transfer proof, not final quality acceptance','resolution':[1024,1024],'samples':8,'cpu_threads':2,'bake_type':'EMIT','lighting_included':False,'margin_pixels':8,'elapsed_seconds':elapsed,'image_bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'mapping_limit':'Generated reconstructed from each original local bound and preserved as an interpolated point attribute; no independent bit-exact ORCO claim.'}
(ROOT/'qa/wood_1024_bake.json').write_text(json.dumps(report,indent=2)+'\n');print('WOOD_1024_PROOF',json.dumps(report))
