"""Reopen a saved Blender artifact in a separate background process and inspect."""
from pathlib import Path
import bpy, json, math
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'A_Page_at_Rest.blend'))
s=bpy.context.scene
external=[]
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:external.append(image.filepath)
for lib in bpy.data.libraries:external.append(lib.filepath)
assert not external
assert s.render.filepath.startswith('//')
assert s.render.threads==2 and s.cycles.device=='CPU'
assert not s.use_nodes
assert all(math.isfinite(c) for ob in s.objects if ob.type=='MESH' for v in ob.data.vertices for c in v.co)
assert len([ob for ob in s.objects if ob.name.endswith('Brass_Cradle')])==2
paper=bpy.data.objects['Left_Page'].data.materials[0]
assert paper==bpy.data.objects['Right_Page'].data.materials[0]
assert not any(n.type=='EMISSION' for n in paper.node_tree.nodes)
result={'reopened':True,'external_dependencies':external,'relative_render_output':s.render.filepath,
        'object_count':len(s.objects),'threads':s.render.threads,'cpu':s.cycles.device=='CPU',
        'camera':s.camera.name,'compositor':s.use_nodes,'non_emissive_paper':True}
(ROOT/'blend_reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
