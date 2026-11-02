"""Read-only source -> derived real-time GLB. Run with source blend already open in background.
Never saves the source blend. No baking, no landscape, no botanical meshes.
"""
import bpy,json,hashlib,sys,re,argparse
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'assets/refuge.glb')
options=parser.parse_args(args)
source=options.source or (Path(bpy.data.filepath) if bpy.data.filepath else ROOT.parent/'glass-refuge'/'Glass_Refuge.blend')
source=source.resolve()
if not source.is_file():raise FileNotFoundError('Pass -- --source /path/to/Glass_Refuge.blend or place the public sibling glass-refuge beside this project.')
if Path(bpy.data.filepath).resolve()!=source:bpy.ops.wm.open_mainfile(filepath=str(source))
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
keep=[];excluded=[]
for ob in bpy.context.scene.objects:ob.hide_render=False
for o in list(bpy.context.scene.objects):
 names=[c.name for c in o.users_collection]
 allowed=any(n.startswith(('01 |','02 |','03 |','04 |','05 |','07 |','09 |')) for n in names)
 if any(n.startswith('06 |') for n in names) and o.name.startswith(('Planter soil','Planter long wall','Planter end')):allowed=True
 if o.type=='MESH' and allowed:keep.append(o)
 else:excluded.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
def bounds(objects):
 pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
 return {'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}
before_bounds=bounds(keep)
# Apply evaluated bevels/solidify only to the in-memory derivative.
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=keep[0];bpy.ops.object.convert(target='MESH')
bpy.context.view_layer.update();converted_bounds=bounds(list(bpy.context.scene.objects))
# Bake-free, intentionally approximate PBR constants. Procedural patterns are NOT exported.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 if m.name.startswith('Oak |') and any(n.type=='TEX_IMAGE' and n.image for n in m.node_tree.nodes):continue # Preserve the verified albedo proof.
 color=tuple(m.diffuse_color);old=m.node_tree.nodes.get('Principled BSDF')
 rough=float(old.inputs['Roughness'].default_value) if old else .5;metal=float(old.inputs['Metallic'].default_value) if old else 0
 m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;m.use_backface_culling=True
 if m.name.startswith('Glass'):
  p.inputs['Base Color'].default_value=(.62,.79,.87,.16);p.inputs['Alpha'].default_value=.16;p.inputs['Transmission Weight'].default_value=0;m.use_backface_culling=False;m.surface_render_method='DITHERED'
 if m.name.startswith('Opal'):
  p.inputs['Emission Color'].default_value=(1,.58,.22,1);p.inputs['Emission Strength'].default_value=1
# Join by material; glass panes retain individual objects for transparency sorting.
groups={};glass_count=0
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 mat=o.data.materials[0].name if o.data.materials else 'None'
 if mat.startswith('Glass'):
  o.name='GlassPane_%02d'%glass_count;glass_count+=1;continue
 if mat.startswith('Opal'):key='PendantGlobe'
 elif o.name.startswith(('Pendant braided','Pendant brass')):key='PendantHardware'
 else:key='Opaque_'+re.sub('[^A-Za-z0-9]+','_',mat.split('|')[0]).strip('_')
 groups.setdefault(key,[]).append(o)
for name,objs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0]
 if len(objs)>1:bpy.ops.object.join()
 bpy.context.object.name=name
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.update()
after=list(bpy.context.scene.objects);after_bounds=bounds(after)
assert max(abs(converted_bounds[k][i]-after_bounds[k][i]) for k in ['min','max'] for i in range(3))<1e-5
# Export selected meshes only. Explicit glTF avoids automatic .blend imports.
out=options.output.resolve();out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False,export_extras=False)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'source_sha256':source_hash,'source_unchanged':True,'source_meshes_kept':len(keep),'excluded_objects':len(excluded),'derived_mesh_objects':len(after),'bounds_blender_z_up_before':converted_bounds,'bounds_blender_z_up_after':after_bounds,'glass_panes':glass_count,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in after),'material_slots':sum(len(o.data.materials) for o in after),'glb_bytes':out.stat().st_size,'simplifications':['No botanical meshes or landscape','Only oak carries the selected albedo proof; other procedural materials remain approximate PBR constants','No source lighting exported; realtime viewer reconstructs lighting','Opaque static pieces merged by material; glass panes and globe remain separate']}
(ROOT/'qa/export_audit.json').write_text(json.dumps(report,indent=2));print('DERIVED_EXPORT_PASS',json.dumps(report))
