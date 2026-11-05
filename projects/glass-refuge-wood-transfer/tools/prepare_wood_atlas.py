"""Derivative-only UV preparation. No source save and no baking in this stage."""
import bpy,json,math,hashlib,sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path)
options=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=(options.source or (Path(bpy.data.filepath) if bpy.data.filepath else ROOT.parent/'glass-refuge'/'Glass_Refuge.blend')).resolve()
if not source.is_file():raise FileNotFoundError('Use -- --source path/to/Glass_Refuge.blend or public sibling ../glass-refuge/Glass_Refuge.blend')
if Path(bpy.data.filepath).resolve()!=source:bpy.ops.wm.open_mainfile(filepath=str(source))
for folder in ('qa','tmp','assets'):(ROOT/folder).mkdir(exist_ok=True)
sha=hashlib.sha256(source.read_bytes()).hexdigest()
wood=bpy.data.materials['Oak | long grain / warm honey'];objects=[o for o in bpy.data.objects if o.type=='MESH' and wood.name in [m.name for m in o.data.materials if m]]
records=[];missing_uv=[]
for o in objects:
 lo=[min(v.co[i] for v in o.data.vertices) for i in range(3)];hi=[max(v.co[i] for v in o.data.vertices) for i in range(3)];span=[hi[i]-lo[i] for i in range(3)]
 assert min(span)>1e-6
 attr=o.data.attributes.new(name='refuge_generated',type='FLOAT_VECTOR',domain='POINT')
 for v,d in zip(o.data.vertices,attr.data):d.vector=tuple((v.co[i]-lo[i])/span[i] for i in range(3))
 if o.data.uv_layers:o.data.uv_layers.active.name='WoodAtlas'
 else:missing_uv.append(o.name)
 records.append({'name':o.name,'bounds_min':lo,'bounds_max':hi})
# Remove object-bound dependency before any evaluation/join. Attributes interpolate through bevel.
n=wood.node_tree.nodes;l=wood.node_tree.links;vm=next(v for v in n if v.bl_idname=='ShaderNodeVectorMath');attrib=n.new('ShaderNodeAttribute');attrib.attribute_name='refuge_generated'
for link in list(vm.inputs[0].links):l.remove(link)
l.new(attrib.outputs['Vector'],vm.inputs[0])
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH')
# Preserve connected cube-net UVs on the 27 prismatic objects. Only five UV-less ribs need unwrap.
for name in missing_uv:
 o=bpy.data.objects[name];bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 uv=o.data.uv_layers.new(name='WoodAtlas');o.data.uv_layers.active=uv;uv.active_render=True
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
 bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.005,area_weight=.5,correct_aspect=True,scale_to_bounds=True)
 bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();oak=bpy.context.object;oak.name='Oak_Baked_Atlas'
assert oak.data.attributes.get('refuge_generated') is not None
uv=oak.data.uv_layers['WoodAtlas'];oak.data.uv_layers.active=uv;uv.active_render=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
# Mesh selection alone does not select old UV loops when UV sync is disabled.
bpy.ops.uv.select_all(action='SELECT')
bpy.ops.uv.average_islands_scale();bpy.ops.uv.pack_islands(rotate=True,margin_method='FRACTION',margin=4/512)
bpy.ops.object.mode_set(mode='OBJECT')
mesh=oak.data;mesh.calc_loop_triangles();uv=mesh.uv_layers.active.data
out={'resolution':512,'source_sha256':sha,'mapping':'Original per-object local bounds normalized to point attribute before modifiers/join. Reconstruction of Generated, not independently proven bit-exact ORCO.','objects':records,'vertices':[list(v.co) for v in mesh.vertices],'polygons':[{'vertices':list(p.vertices),'uv':[list(uv[i].uv) for i in p.loop_indices],'area':p.area} for p in mesh.polygons],'triangles':[{'polygon':t.polygon_index,'uv':[list(uv[i].uv) for i in t.loops]} for t in mesh.loop_triangles]}
(ROOT/'qa/wood_uv_raw.json').write_text(json.dumps(out))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tmp/wood_prebake.blend'),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print('WOOD_UV_PREPARED',len(objects),len(mesh.polygons),len(mesh.loop_triangles))
