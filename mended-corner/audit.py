"""Read-only Blender scene audit. Writes JSON, never saves the inspected .blend.

TMPDIR="$PWD/work" blender -b Mended_Corner.blend -t 2 --python audit.py
Geometric checks are visual-asset checks, not woodworking or safety certification.
"""
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
scene=bpy.context.scene
depsgraph=bpy.context.evaluated_depsgraph_get()
records=[]
all_world={}
for ob in scene.objects:
    if ob.type!='MESH':continue
    evaluated=ob.evaluated_get(depsgraph)
    me=evaluated.to_mesh()
    verts=[ob.matrix_world@v.co for v in me.vertices]
    all_world[ob.name]=verts
    finite=all(math.isfinite(c) for v in verts for c in v)
    bm=bmesh.new();bm.from_mesh(me)
    non_manifold=sum(not edge.is_manifold for edge in bm.edges)
    zero_area=sum(face.calc_area()<1e-12 for face in bm.faces)
    volume=bm.calc_volume(signed=True) if non_manifold==0 else None
    records.append({'name':ob.name,'vertices':len(verts),'faces':len(me.polygons),
                    'finite_coordinates':finite,'non_manifold_edges':non_manifold,
                    'zero_area_faces':zero_area,'signed_local_volume':volume})
    bm.free();evaluated.to_mesh_clear()

def bounds(names):
    points=[point for name in names for point in all_world[name]]
    return {'minimum':[min(p[k] for p in points) for k in range(3)],
            'maximum':[max(p[k] for p in points) for k in range(3)]}

plane_names=[name for name in all_world if name.startswith('Plane |')]
pencil_names=[name for name in all_world if name.startswith('Pencil |')]
plane_bounds=bounds(plane_names);pencil_bounds=bounds(pencil_names)
seat_z=.49
plane_gap=plane_bounds['minimum'][2]-seat_z
pencil_gap=pencil_bounds['minimum'][2]-seat_z
cloth_name='PROP · Neighbour’s sage throw | continuous drape'
cloth_over_seat=[v for v in all_world[cloth_name] if -.24<=v.y<=.23]
cloth_gap=min(v.z for v in cloth_over_seat)-seat_z
repair_bounds=bounds(['Quiet fitted repair | shallow pale splice'])
bearer_names=[name for name in all_world if name.startswith('Bench under-seat bearer')]
bearer_top=max(all_world[name][i].z for name in bearer_names for i in range(len(all_world[name])))
reference=ROOT/'reference/gpt_image_concept.png'
reference_bytes=reference.read_bytes()
reference_sha=hashlib.sha256(reference_bytes).hexdigest()
packed=bpy.data.images.get('REFERENCE ONLY · GPT Image concept')
packed_data=bytes(packed.packed_file.data) if packed and packed.packed_file else b''
texture_images=[]
for material in bpy.data.materials:
    if not material.use_nodes:continue
    for node in material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image:texture_images.append(node.image.name)
absolute_image_paths=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.filepath.startswith('//')]
external_libraries=[lib.filepath for lib in bpy.data.libraries]
main_file=Path(bpy.data.filepath)
report={
 'inspected_file':main_file.name,
 'blender_version':bpy.app.version_string,
 'mesh_objects':len(records),
 'curve_objects':sum(ob.type=='CURVE' for ob in scene.objects),
 'collections':len(scene.collection.children),
 'evaluated_mesh_vertices':sum(item['vertices'] for item in records),
 'finite_coordinates':all(item['finite_coordinates'] for item in records),
 'zero_area_faces':sum(item['zero_area_faces'] for item in records),
 'non_manifold_meshes':[item['name'] for item in records if item['non_manifold_edges']],
 'negative_volume_closed_meshes':[item['name'] for item in records if item['signed_local_volume'] is not None and item['signed_local_volume']<0],
 'contact_measurements_m':{
   'plane_lowest_point_minus_seat_top':plane_gap,
   'pencil_lowest_point_minus_seat_top':pencil_gap,
   'throw_lowest_evaluated_point_over_seat_minus_seat_top':cloth_gap,
   'repair_top_minus_seat_top':repair_bounds['maximum'][2]-seat_z,
   'bearer_top_minus_seat_underside':bearer_top-.456,
 },
 'reference_sha256':reference_sha,
 'packed_reference_matches_original':packed_data==reference_bytes,
 'image_texture_nodes':texture_images,
 'absolute_image_paths':absolute_image_paths,
 'linked_external_libraries':external_libraries,
 'render':{'engine':scene.render.engine,'device':scene.cycles.device,'threads':scene.render.threads,
           'resolution':[scene.render.resolution_x,scene.render.resolution_y],
           'resolution_percentage':scene.render.resolution_percentage,'samples':scene.cycles.samples,
           'denoising':scene.cycles.use_denoising,'path':scene.render.filepath},
 'checks':{
   'all_mesh_coordinates_finite':all(item['finite_coordinates'] for item in records),
   'no_zero_area_mesh_faces':all(item['zero_area_faces']==0 for item in records),
   'all_evaluated_meshes_closed':all(item['non_manifold_edges']==0 for item in records),
   'closed_mesh_winding_outward':all(item['signed_local_volume'] is None or item['signed_local_volume']>0 for item in records),
   'plane_contacts_seat':-.0005<=plane_gap<=.001,
   'pencil_contacts_seat':-.0005<=pencil_gap<=.001,
   'throw_has_near_contact_with_seat':-.001<=cloth_gap<=.002,
   'repair_top_flush':abs(repair_bounds['maximum'][2]-seat_z)<.00001,
   'bearers_touch_seat_underside':abs(bearer_top-.456)<.00001,
   'reference_packed_byte_identical':packed_data==reference_bytes,
   'no_reference_projection_or_external_textures':not texture_images,
   'relative_render_and_image_paths':scene.render.filepath.startswith('//') and not absolute_image_paths,
   'no_linked_external_libraries':not external_libraries,
   'cpu_at_most_two_threads':scene.cycles.device=='CPU' and scene.render.threads_mode=='FIXED' and scene.render.threads<=2,
 },
 'limitations':[
   'Tests inspect meshes after modifiers, not structural strength or safe construction.',
   'Contact tests use selected surface extrema; they do not certify every pairwise intersection or a physical cloth solution.',
   'Plane components and bench joinery have intentional hidden overlaps.',
   'Curves are renderable decorative yarn, rain and lamp wires; only mesh topology is audited.',
   'Glazing shadow visibility and area-light ray visibility are artistic noise-control approximations.',
 ],
 'meshes':records,
}
report['all_assertions_pass']=all(report['checks'].values())
output=ROOT/('draft_audit.json' if 'Draft' in main_file.name else 'geometry_audit.json')
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({key:report[key] for key in ('inspected_file','mesh_objects','curve_objects','evaluated_mesh_vertices','contact_measurements_m','checks','all_assertions_pass')},ensure_ascii=False,indent=2))
assert report['all_assertions_pass'], 'Scene audit failed; inspect geometry_audit.json or draft_audit.json'
