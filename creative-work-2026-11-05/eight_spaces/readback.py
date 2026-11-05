import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'Eight-Spaces.blend'))
s=bpy.context.scene
warps=[o for o in s.objects if o.name.startswith('warp ')];wefts=[o for o in s.objects if o.name.startswith('weft ')]
assert len(warps)==len(wefts)==17
assert all(o.type=='MESH' and o.animation_data is None for o in warps+wefts)
assert s.render.resolution_x==s.render.resolution_y==1200 and s.cycles.samples==128
assert s.camera.data.type=='ORTHO' and abs(s.camera.data.ortho_scale-5.3)<1e-5
assert s.render.filepath=='//Eight-Spaces.png'
assert not [im for im in bpy.data.images if im.source=='FILE' and im.filepath]
q=json.loads((P/'geometry-check.json').read_text());assert q['crossings']==289 and q['evaluated_mesh_overlap_pairs']==[]
cfg=json.loads((P/'build-config.json').read_text());assert cfg['source_sha256']==hashlib.sha256((P/'build.py').read_bytes()).hexdigest()
r={'objects':len(s.objects),'warp_strips':17,'weft_strips':17,'gold_strips':sum(o.data.materials[0].name=='Ochre paper with a longer span' for o in wefts),'resolution':[1200,1200],'samples':128,'denoising':s.cycles.use_denoising,'camera_type':s.camera.data.type,'external_images':0,'saved_render_path':s.render.filepath,'source_hash_matches_build':True,'geometry_check_matches_counts':True}
(P/'readback.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
