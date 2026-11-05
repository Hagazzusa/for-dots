"""Read-only Blender data audit; writes measured findings next to source."""
import bpy,bmesh,json,math
from pathlib import Path
root=Path(__file__).resolve().parent
report={'mesh_count':0,'arch_solids':[],'non_finite_vertices':[],'zero_area_faces':0,'collections':[]}
for c in bpy.data.collections:report['collections'].append({'name':c.name,'objects':len(c.objects)})
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 report['mesh_count']+=1
 if any(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices):report['non_finite_vertices'].append(o.name)
 bm=bmesh.new();bm.from_mesh(o.data)
 report['zero_area_faces']+=sum(f.calc_area()<1e-12 for f in bm.faces)
 if o.name.startswith('Rib') and ('curved oak' in o.name or 'weather cap' in o.name) or o.name.startswith('Roof glazing'):
  volume=bm.calc_volume(signed=True)
  report['arch_solids'].append({'name':o.name,'signed_volume':round(volume,8),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)})
 bm.free()
report['arch_normals_outward']=all(i['signed_volume']>0 for i in report['arch_solids'])
report['arch_solids_closed']=all(i['nonmanifold_edges']==0 for i in report['arch_solids'])
report['packed_reference']=bpy.data.images.get('gpt_image_concept.png').packed_file is not None
report['camera']=bpy.context.scene.camera.name
report['cycles_denoising']=bpy.context.scene.cycles.use_denoising
report['glass_roughness']=bpy.data.materials['Glass | rain-softened low-iron 6mm'].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value
report['samples']=bpy.context.scene.cycles.samples
report['clamp_direct']=bpy.context.scene.cycles.sample_clamp_direct
report['clamp_indirect']=bpy.context.scene.cycles.sample_clamp_indirect
report['reflective_caustics']=bpy.context.scene.cycles.caustics_reflective
report['refractive_caustics']=bpy.context.scene.cycles.caustics_refractive
report['render_dimensions']=[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y,bpy.context.scene.render.resolution_percentage]
report['limitations']='Mesh closure and signed volume do not validate structure, glazing safety, drainage, or code compliance.'
(root/'geometry_audit.json').write_text(json.dumps(report,indent=2))
assert report['arch_normals_outward'] and report['arch_solids_closed'] and not report['non_finite_vertices'] and report['packed_reference']
print('GEOMETRY_AUDIT_PASS',report['mesh_count'],len(report['arch_solids']))
