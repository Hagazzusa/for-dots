"""Read an immutable A Page at Rest source, export evaluated geometry for a viewer.

Run in Blender 4.3.2 with --python-exit-code 1:
  blender -b -t 2 --python export_from_blender.py -- --source ../page-at-rest/A_Page_at_Rest.blend
This script never saves the source .blend or writes into its directory.
"""
import bpy
import argparse
import hashlib
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path
from mathutils import Matrix, Quaternion, Vector

ROOT=Path(__file__).resolve().parent
EXPECTED_SOURCE_SHA256='4d0ee8b68c98381dfb89e68bd77b3b85ef6d29c716d97d6c2e78f7893937a72e'
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,required=True)
parser.add_argument('--verify-only',action='store_true',help='Audit the existing GLB without replacing it.')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=args.source.resolve()
sha=lambda data:hashlib.sha256(data).hexdigest()
before=sha(source.read_bytes())
assert before==EXPECTED_SOURCE_SHA256,'Source does not match the reviewed immutable artwork.'
for name in ('assets','work'): (ROOT/name).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=2
deps=bpy.context.evaluated_depsgraph_get()

# Original runtime material approximations, not Cycles shader baking.
PBR={
 'PR_Walnut':{'base_color_linear':[.15,.068,.026,1],'metallic':0,'roughness':.48},
 'PR_Brass':{'base_color_linear':[.42,.27,.105,1],'metallic':.76,'roughness':.34},
 'PR_Paper_Opaque_Backlight_Target':{'base_color_linear':[.74,.63,.45,1],'metallic':0,'roughness':.88},
 'PR_Linen':{'base_color_linear':[.30,.28,.235,1],'metallic':0,'roughness':.85},
 'PR_Book_Paper':{'base_color_linear':[.55,.48,.37,1],'metallic':0,'roughness':.88},
}
mats={}
for name,spec in PBR.items():
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=spec['base_color_linear'];m.use_backface_culling=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=spec['base_color_linear']
    p.inputs['Metallic'].default_value=spec['metallic'];p.inputs['Roughness'].default_value=spec['roughness']
    p.inputs['Transmission Weight'].default_value=0;p.inputs['Coat Weight'].default_value=0
    p.inputs['IOR'].default_value=1.5
    mats[name]=m

MAP=[
 ('Walnut_Base','WalnutBase','PageSculpture','PR_Walnut'),
 ('Left_Brass_Cradle','LeftBrassCradle','PageSculpture','PR_Brass'),
 ('Right_Brass_Cradle','RightBrassCradle','PageSculpture','PR_Brass'),
 ('Left_Page','LeftPage','PageSculpture','PR_Paper_Opaque_Backlight_Target'),
 ('Right_Page','RightPage','PageSculpture','PR_Paper_Opaque_Backlight_Target'),
 ('One small linen book — lower cover','BookLowerCover','LinenBook','PR_Linen'),
 ('One small linen book — pages','BookPages','LinenBook','PR_Book_Paper'),
 ('One small linen book — upper cover','BookUpperCover','LinenBook','PR_Linen'),
 ('One small linen book — spine','BookSpine','LinenBook','PR_Linen'),
]
collection=bpy.data.collections.new('EXPORT_ONLY · runtime derivative')
scene.collection.children.link(collection)
groups={}
for name in sorted({x[2] for x in MAP}):
    ob=bpy.data.objects.new(name,None);collection.objects.link(ob);groups[name]=ob
    ob['role']='context_book' if name=='LinenBook' else 'hero_sculpture'
def to_yup(v):return Vector((v.x,v.z,-v.y))
def bounds(points):return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
def quant(v):return tuple(round(float(x),7) for x in v)
def triangle_signature(points,triangles):
    # Ignore triangle order, corner rotation and duplicate seam vertices, while
    # preserving winding: a reversed triangle is not considered equivalent.
    result=Counter()
    for tri in triangles:
        a,b,c=(quant(points[i]) for i in tri)
        result[min((a,b,c),(b,c,a),(c,a,b))]+=1
    return result
def volume(points,triangles):return sum(points[a].dot(points[b].cross(points[c]))/6 for a,b,c in triangles)
sources={}; exports=[]
for original,name,group,material in MAP:
    src=bpy.data.objects[original];evaluated=src.evaluated_get(deps)
    me=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
    me.transform(src.matrix_world);me.update();me.name=name+'_Geometry'
    me.calc_loop_triangles()
    pts=[to_yup(v.co) for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
    sources[name]={'points':pts,'triangles':tris,'original':original,'bounds':bounds(pts),
                   'volume':volume(pts,tris),'signature':triangle_signature(pts,tris)}
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);ob.parent=groups[group]
    me.materials.clear();me.materials.append(mats[material])
    for poly in me.polygons:poly.material_index=0
    ob['source_component']=original;ob['runtime_material']=material
    exports.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in exports+list(groups.values()):ob.select_set(True)
bpy.context.view_layer.objects.active=exports[0]
output=ROOT/'assets/page_at_rest.glb'
if not args.verify_only:
    bpy.ops.export_scene.gltf(filepath=str(output),check_existing=False,export_format='GLB',
     use_selection=True,export_apply=False,export_yup=True,export_normals=True,
     export_texcoords=False,export_tangents=False,export_materials='EXPORT',
     export_cameras=False,export_lights=False,export_animations=False,export_skins=False,
     export_morph=False,export_extras=True,export_unused_images=False,export_unused_textures=False,
     export_draco_mesh_compression_enable=False,export_use_gltfpack=False,will_save_settings=False)

# Read the actual GLB binary, resolve its node transforms and compare its actual
# triangle positions to evaluated source meshes. No round-trip claim from counts alone.
data=output.read_bytes();magic,version,length=struct.unpack_from('<4sII',data,0)
assert magic==b'glTF' and version==2 and length==len(data)
at=12;doc=None;binary=None
while at<len(data):
    size,kind=struct.unpack_from('<II',data,at);payload=data[at+8:at+8+size];at+=8+size
    if kind==0x4E4F534A:doc=json.loads(payload)
    elif kind==0x004E4942:binary=payload
assert doc is not None and binary is not None
components={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def accessor(index):
    acc=doc['accessors'][index];view=doc['bufferViews'][acc['bufferView']]
    code,size=components[acc['componentType']];width=widths[acc['type']]
    offset=view.get('byteOffset',0)+acc.get('byteOffset',0);stride=view.get('byteStride',size*width)
    return [struct.unpack_from('<'+code*width,binary,offset+i*stride) for i in range(acc['count'])]
def transform(node):
    if 'matrix' in node:
        m=node['matrix'];return Matrix([[m[col*4+row] for col in range(4)] for row in range(4)])
    t=Matrix.Translation(node.get('translation',[0,0,0]));q=node.get('rotation',[0,0,0,1])
    r=Quaternion((q[3],q[0],q[1],q[2])).to_matrix().to_4x4();s=node.get('scale',[1,1,1])
    return t@r@Matrix.Diagonal((*s,1))
records=[];all_points=[];actual_points={}
def visit(index,parent):
    node=doc['nodes'][index];world=parent@transform(node)
    if 'mesh' in node:
        name=node['name'];original=sources[name];points=[];triangles=[];normal_count=0
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            assert primitive.get('mode',4)==4
            offset=len(points);points += [world@Vector(x) for x in accessor(primitive['attributes']['POSITION'])]
            ids=[x[0]+offset for x in accessor(primitive['indices'])]
            triangles += [tuple(ids[i:i+3]) for i in range(0,len(ids),3)]
            normals=accessor(primitive['attributes']['NORMAL']);normal_count+=len(normals)
            assert all(all(math.isfinite(c) for c in n) and .98<Vector(n).length<1.02 for n in normals)
        source_set=set(quant(p) for p in original['points']);target_set=set(quant(p) for p in points)
        same_positions=source_set==target_set
        same_triangles=original['signature']==triangle_signature(points,triangles)
        vb=volume(points,triangles);delta=abs(vb-original['volume'])
        rec={'name':name,'source_component':original['original'],'source_evaluated_vertices':len(original['points']),
             'exported_vertices_including_normal_seams':len(points),'source_triangles':len(original['triangles']),
             'exported_triangles':len(triangles),'bounds_y_up_m':bounds(points),
             'identical_unique_positions_at_0_1_micrometre':same_positions,
             'identical_oriented_triangle_position_multiset_at_0_1_micrometre':same_triangles,
             'signed_source_volume_m3':original['volume'],'signed_exported_volume_m3':vb,
             'absolute_volume_delta_m3':delta,'unit_finite_normals':normal_count==len(points)}
        records.append(rec);all_points.extend(points);actual_points[name]=points
    for child in node.get('children',[]):visit(child,world)
for index in doc['scenes'][doc.get('scene',0)]['nodes']:visit(index,Matrix.Identity(4))
after=sha(source.read_bytes())
overall=bounds(all_points)
hero_points=[p for name,pts in actual_points.items() if name in {'WalnutBase','LeftBrassCradle','RightBrassCradle','LeftPage','RightPage'} for p in pts]
checks={
 'immutable_source_sha_before_and_after':before==after==EXPECTED_SOURCE_SHA256,
 'nine_expected_mesh_components':set(actual_points)==set(sources) and len(records)==9,
 'sculpture_and_context_book_groups':set(groups)=={'PageSculpture','LinenBook'},
 'all_source_positions_preserved_to_0_1_micrometre':all(r['identical_unique_positions_at_0_1_micrometre'] for r in records),
 'all_source_oriented_triangle_geometry_preserved_to_0_1_micrometre':all(r['identical_oriented_triangle_position_multiset_at_0_1_micrometre'] for r in records),
 'all_triangle_counts_preserved':all(r['source_triangles']==r['exported_triangles'] for r in records),
 'outward_signed_volumes_preserved':all(r['signed_exported_volume_m3']>0 and r['absolute_volume_delta_m3']<1e-8 for r in records),
 'all_normals_finite_and_unit':all(r['unit_finite_normals'] for r in records),
 'no_images_or_textures':not doc.get('images') and not doc.get('textures'),
 'no_cameras_lights_or_animations':not doc.get('cameras') and not doc.get('animations') and 'KHR_lights_punctual' not in doc.get('extensions',{}),
 'no_external_buffer_uris':all('uri' not in b for b in doc['buffers']),
 'five_named_pbr_materials':set(m['name'] for m in doc['materials'])==set(PBR),
 'opaque_materials_without_optical_extensions':all(m.get('alphaMode','OPAQUE')=='OPAQUE' and not m.get('extensions') for m in doc['materials']),
}
report={'producer_blend_filename':source.name,'producer_blend_sha256':before,
 'blender_version':bpy.app.version_string,'gltf_generator':doc['asset'].get('generator'),
 'output':'assets/page_at_rest.glb','output_sha256':sha(data),'output_bytes':len(data),
 'axis_transform':'Blender (x,y,z) -> glTF/Godot (x,z,-y)','units':'metres','recommended_root_scale':[1,1,1],
 'origin':'Centre of walnut base bottom; supporting tabletop plane Y=0.',
 'bounds_y_up_m':overall,'hero_bounds_y_up_m':bounds(hero_points),
 'recommended_original_view':{'camera_position':[.33,.315,.74],'look_at':[.023,.113,-.025],'vertical_fov_degrees':math.degrees(2*math.atan(36/(2*68*1.5)))},
 'concealed_source_position_y_up_m':[0,.073,-.042],
 'mesh_components':len(records),'triangles':sum(r['exported_triangles'] for r in records),
 'materials':PBR,'checks':checks,'all_assertions_pass':all(checks.values()),'components':records,
 'optical_limits':['Uniform core PBR defaults, not the procedural Cycles shaders.',
 'The GLB paper is opaque. Godot may replace it with a documented BACKLIGHT shader approximation; this is not traced transmission, refraction or a physically equivalent Cycles material.',
 'The complete finite-thickness paper surfaces, brass and walnut source geometry are preserved; no generated concept or rendered image is projected onto geometry.',
 'Metal needs sky radiance/reflection lighting; ambient diffuse lighting alone is insufficient.',
 'No source cyclorama, lamps, camera, animation or outside texture is included.']}
(ROOT/'export_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['all_assertions_pass'],'Export comparison failed; inspect export_audit.json'
print(json.dumps({k:report[k] for k in ('output','output_sha256','output_bytes','bounds_y_up_m','hero_bounds_y_up_m','mesh_components','triangles','checks','all_assertions_pass')},ensure_ascii=False,indent=2))
