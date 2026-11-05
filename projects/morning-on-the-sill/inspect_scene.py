"""Background native reopen; source unchanged, QA JSON written. Blender 4.3.2."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;P=json.loads((ROOT/'parameters.json').read_text());source=ROOT/'Morning_on_the_Sill.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
assert s.render.filepath=='//renders/morning_on_the_sill_final.png'
assert s.render.threads==2 and s.cycles.device=='CPU' and s.cycles.samples==P['render']['final_samples']
assert [s.render.resolution_x,s.render.resolution_y]==[P['render']['final_width'],P['render']['final_height']]
assert s['ParametersSha256']==hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest()
assert s['BuildSourceSha256']==hashlib.sha256((ROOT/'build.py').read_bytes()).hexdigest()
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]+[lib.filepath for lib in bpy.data.libraries];assert not external
cat=bpy.data.objects['Cat — unified hand-shaped stoneware'];bm=bmesh.new();bm.from_mesh(cat.data);assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=False);assert vol>0
remaining=set(bm.verts);components=0
while remaining:
 components+=1;todo=[remaining.pop()]
 while todo:
  v=todo.pop()
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in remaining:remaining.remove(w);todo.append(w)
bm.free();assert components==1
contact=min((cat.matrix_world@v.co).z for v in cat.data.vertices);assert abs(contact)<1e-7
sources=bpy.data.collections['Editable cat construction sources — hidden'];assert sources.hide_render and len(sources.objects)==8
leaves=[bpy.data.objects[n] for n in ['Ochre ginkgo fan','Olive ginkgo fan']];deps=bpy.context.evaluated_depsgraph_get();leaf_checks=[]
for ob in leaves:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=False);assert volume>0;bm.free();ev.to_mesh_clear()
 stem=bpy.data.objects[ob.name[:-4]+' fine resting stem'];ev=stem.evaluated_get(deps);me=ev.to_mesh();gap=min((stem.matrix_world@v.co).z for v in me.vertices);assert abs(gap)<.0001;ev.to_mesh_clear()
 leaf_checks.append({'name':ob.name,'evaluated_closed_manifold':True,'volume_m3':volume,'stem_floor_gap_m':gap,'solidify_thickness_m':ob.modifiers['Thin leaf lamina'].thickness})
finite=0
for ob in s.objects:
 if ob.type in ('MESH','CURVE'):
  ev=ob.evaluated_get(deps);me=ev.to_mesh();assert all(math.isfinite(c) for v in me.vertices for c in v.co);finite+=1;ev.to_mesh_clear()
assert not s.use_nodes
result={'reopened':True,'input_blend_sha256':before,'input_blend_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before,'source_parameters_and_build_hashes_match':True,'external_dependencies':external,'relative_render_path':s.render.filepath,'cat_closed_manifold':True,'cat_connected_components':components,'cat_volume_m3':vol,'cat_floor_contact_gap_m':contact,'hidden_editable_construction_sources':len(sources.objects),'leaf_checks':leaf_checks,'finite_evaluated_mesh_and_curve_objects':finite,'cpu_threads':2,'final_resolution':[s.render.resolution_x,s.render.resolution_y],'max_samples':s.cycles.samples,'native_gui_tested':False,'limitations':'Background native/file/virtual geometry checks only. Not ceramic manufacturing, botanical, architectural or physical safety validation.'}
assert result['input_blend_unchanged'];(ROOT/'reopen_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
