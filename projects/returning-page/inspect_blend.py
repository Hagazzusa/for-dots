import bpy, json, math, hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Returning_Page.blend'))
o=bpy.data.objects['Returning Page - CAD brass']; p=json.loads((R/'cad/bookmark_mesh.json').read_text())
assert len(o.data.vertices)==len(p['vertices']) and len(o.data.polygons)==len(p['faces'])
err=max(abs(o.data.vertices[i].co[k]-v[k]*.001) for i,v in enumerate(p['vertices']) for k in range(3)); assert err<1e-8
assert o['mesh_sha256']==hashlib.sha256((R/'cad/bookmark_mesh.json').read_bytes()).hexdigest()
assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
r={'blend_reopened':True,'cad_mesh_hash_matches':True,'all_vertices_finite':True,'max_vertex_error_m':err,'cad_vertices':len(o.data.vertices),'cad_triangles':len(o.data.polygons),'bookmark_modifiers':len(o.modifiers),'no_bookmark_remodeling':len(o.modifiers)==0,'camera':bpy.context.scene.camera.name,'materials':len(bpy.data.materials)}
(R/'blend_reopen_validation.json').write_text(json.dumps(r,indent=2)+'\n'); print(r)
