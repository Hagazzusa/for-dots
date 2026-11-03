import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent

def snapshot(file):
 bpy.ops.wm.open_mainfile(filepath=str(R/file));s=bpy.context.scene
 def val(v):
  try:return list(v)
  except:return v
 def nodes(tree):return {n.name:{'type':n.bl_idname,'operation':getattr(n,'operation',None),'inputs':[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]} for n in tree.nodes}
 return {'objects':{o.name:{'matrix':[list(x) for x in o.matrix_world],'hidden':o.hide_render,'mesh_sha':hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])).encode()).hexdigest() if o.type=='MESH' else None} for o in s.objects},'materials':{m.name:nodes(m.node_tree) for m in bpy.data.materials if m.use_nodes},'world':nodes(s.world.node_tree),'render':[s.cycles.samples,s.cycles.seed,s.cycles.use_denoising,s.cycles.use_adaptive_sampling,s.render.resolution_x,s.render.resolution_y,s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.camera.data.lens,s.camera.data.dof.use_dof]}
a=snapshot('Cloud_Study.blend');b=snapshot('Cloud_Study_Corrected_Sign.blend');diff=[]
for k in a:
 if a[k]!=b[k]:diff.append(k)
assert diff==['world'],diff
worlddiff=[k for k in a['world'] if a['world'][k]!=b['world'][k]];assert len(worlddiff)==1
(R/'pair_validation.json').write_text(json.dumps({'compared':'Recorded object transforms/mesh coordinates and faces/render hidden states, shader node types/inputs, world node inputs and listed render controls. Not exhaustive .blend proof.','changed_sections':diff,'changed_world_nodes':{k:{'before':a['world'][k],'after':b['world'][k]} for k in worlddiff},'reopened_both':True,'native_saved':False},indent=2)+'\n')
