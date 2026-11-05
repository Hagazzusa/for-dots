"""Read-only audit of the saved Blender scene; only the JSON report is written.

TMPDIR="$PWD/work" blender -b The_Second_Cup.blend -t 2 --python audit.py
Numerical image-asset tests, not product, food, thermal or safety validation.
"""
import bpy
import bmesh
import math
import json
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
scene=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
records=[]; world={}
for ob in scene.objects:
    if ob.type!='MESH': continue
    evaluated=ob.evaluated_get(deps); me=evaluated.to_mesh()
    vertices=[ob.matrix_world@v.co for v in me.vertices]; world[ob.name]=vertices
    bm=bmesh.new(); bm.from_mesh(me)
    edges=sum(not e.is_manifold for e in bm.edges)
    rec={'name':ob.name,'vertices':len(vertices),'faces':len(me.polygons),
         'finite_coordinates':all(math.isfinite(c) for p in vertices for c in p),
         'non_manifold_edges':edges,'zero_area_faces':sum(f.calc_area()<1e-13 for f in bm.faces),
         'signed_local_volume':bm.calc_volume(signed=True) if not edges else None}
    records.append(rec); bm.free(); evaluated.to_mesh_clear()

def ray(ob, origin, direction):
    inverse=ob.matrix_world.inverted(); point=inverse@Vector(origin)
    vector=(inverse.to_3x3()@Vector(direction)).normalized()
    hit,loc,normal,index=ob.ray_cast(point,vector)
    assert hit, 'Required ray missed '+ob.name
    return ob.matrix_world@loc

contacts={}
cups=[]
for ob in scene.objects:
    if ob.get('role') in ('cup_body','bread_plate','kettle_contact'):
        contacts[ob.name]=min(p.z for p in world[ob.name])
    if ob.get('role')=='cup_body':
        x,y=ob['center_xy']
        top_hit=ray(ob,(x,y,.20),(0,0,-1))
        lower_hit=ray(ob,(x,y,-.02),(0,0,1))
        outer=ray(ob,(x+.10,y,.055),(-1,0,0))
        inner=ray(ob,(x,y,.055),(1,0,0))
        wall=outer.x-inner.x
        rim_radii=[math.hypot(p.x-x,p.y-y) for p in world[ob.name] if abs(p.z-.068)<1e-6]
        cups.append({'name':ob.name,'inside_center_ray_floor_z':top_hit.z,'underside_center_ray_z':lower_hit.z,
                     'base_center_thickness_m':top_hit.z-lower_hit.z,'side_wall_thickness_at_z055_m':wall,
                     'rim_wall_thickness_at_z068_m':max(rim_radii)-min(rim_radii),
                     'highest_rim_z':max(p.z for p in world[ob.name]),
                     'inside_clear_to_floor':abs(top_hit.z-.012)<1e-5})

inner_profile=[(.012,.020),(.013,.028),(.015,.032),(.019,.036),(.028,.040),(.041,.043),(.055,.045),(.068,.046),(.0715,.046),(.0734,.0465),(.0744,.0472),(.0748,.0481)]
def inner_radius(z):
    for (za,ra),(zb,rb) in zip(inner_profile,inner_profile[1:]):
        if za<=z<=zb: return ra+(rb-ra)*(z-za)/(zb-za)
    return 0
handle_intrusions={}
for ob in scene.objects:
    if ob.get('role')!='cup_handle': continue
    x,y=ob['cup_center_xy']
    intrusions=[inner_radius(p.z)-math.hypot(p.x-x,p.y-y) for p in world[ob.name] if .012<p.z<.0748]
    handle_intrusions[ob.name]=max([0]+intrusions)

liquid=next(ob for ob in scene.objects if ob.get('role')=='liquid')
tea_vertices=world[liquid.name]
near=next(ob for ob in scene.objects if ob.get('role')=='cup_body' and ob.name.startswith('Near'))
x,y=near['center_xy']
surface=ray(liquid,(x,y,.20),(0,0,-1)).z
flat=[p.z for p in tea_vertices if math.hypot(p.x-x,p.y-y)<=.04001 and p.z>.05]
tea_report={'center_surface_z':surface,'flat_surface_height_range':max(flat)-min(flat),
            'maximum_meniscus_z':max(p.z for p in tea_vertices),'meniscus_rise_m':max(p.z for p in tea_vertices)-surface,
            'liquid_below_rim_m':max(p.z for p in world[near.name])-max(p.z for p in tea_vertices),
            'liquid_floor_clearance_m':min(p.z for p in tea_vertices)-.012,
            'liquid_object_count':sum(ob.get('role')=='liquid' for ob in scene.objects)}

spout=next(ob for ob in scene.objects if ob.get('role')=='spout')
mouth=Vector(spout['mouth_center_world']); axis=Vector(spout['mouth_axis_world']).normalized()
mouth_vertices=[p for p in world[spout.name] if abs((p-mouth).dot(axis))<1e-6]
mouth_radii=[(p-mouth).length for p in mouth_vertices]
inverse=spout.matrix_world.inverted(); origin=mouth+axis*.015
hit,loc,normal,index=spout.ray_cast(inverse@origin,(inverse.to_3x3()@(-axis)).normalized())
distance=(spout.matrix_world@loc-origin).length if hit else None
spout_report={'mouth_wall_thickness_m':max(mouth_radii)-min(mouth_radii),
              'mouth_outer_radius_m':max(mouth_radii),'mouth_inner_radius_m':min(mouth_radii),
              'mouth_center_ray_hit_distance_from_15mm_outside':distance,
              'center_ray_passes_open_lip':distance is None or distance>.016}

# Local spacing of the round vessel/plate bodies; handles and kettle assemblies
# are checked visually, not falsely claimed as exhaustive pairwise collision tests.
centers={}
for ob in scene.objects:
    if ob.get('role') in ('cup_body','bread_plate'):
        points=world[ob.name]
        x=(max(p.x for p in points)+min(p.x for p in points))/2
        y=(max(p.y for p in points)+min(p.y for p in points))/2
        centers[ob.name]=(x,y,max(math.hypot(p.x-x,p.y-y) for p in points))
spacing={}
names=list(centers)
for i,a in enumerate(names):
    for b in names[i+1:]:
        x,y,r=centers[a]; xx,yy,rr=centers[b]
        spacing[a+' / '+b]=math.hypot(x-xx,y-yy)-r-rr

reference=(ROOT/'reference/gpt_image_concept.png').read_bytes()
packed=bpy.data.images.get('REFERENCE ONLY · original GPT Image concept')
packed_bytes=bytes(packed.packed_file.data) if packed and packed.packed_file else b''
textures=[]
for material in bpy.data.materials:
    if material.use_nodes:
        textures += [n.image.name for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
for owner in (scene.world,scene):
    tree=getattr(owner,'node_tree',None)
    if tree: textures += [n.image.name for n in tree.nodes if n.type in ('TEX_IMAGE','TEX_ENVIRONMENT','IMAGE') and getattr(n,'image',None)]
absolute_paths=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.filepath.startswith('//')]
packed_absolute_paths=[pf.filepath for im in bpy.data.images for pf in im.packed_files if pf.filepath and not pf.filepath.startswith('//') and Path(pf.filepath).is_absolute()]
blend_bytes=Path(bpy.data.filepath).read_bytes()
checks={
 'all_mesh_coordinates_finite':all(r['finite_coordinates'] for r in records),
 'all_meshes_closed_after_modifiers':all(r['non_manifold_edges']==0 for r in records),
 'no_zero_area_faces':all(r['zero_area_faces']==0 for r in records),
 'outward_winding':all(r['signed_local_volume'] is not None and r['signed_local_volume']>0 for r in records),
 'five_prop_groups':scene.get('hero_prop_count')==5 and sum(ob.get('role')=='cup_body' for ob in scene.objects)==2 and sum(ob.get('role')=='bread_plate' for ob in scene.objects)==2 and sum(ob.get('role')=='kettle_body' for ob in scene.objects)==1,
 'five_supports_touch_table':len(contacts)==5 and all(abs(z)<1e-6 for z in contacts.values()),
 'both_cups_are_open_to_inner_floor':len(cups)==2 and all(c['inside_clear_to_floor'] for c in cups),
 'both_cups_have_real_base_and_wall':all(.0065<c['base_center_thickness_m']<.0075 and .0037<c['side_wall_thickness_at_z055_m']<.0043 and .0037<c['rim_wall_thickness_at_z068_m']<.0043 for c in cups),
 'cup_handles_do_not_enter_inner_bowls':len(handle_intrusions)==2 and all(depth<.00001 for depth in handle_intrusions.values()),
 'only_one_cup_contains_liquid':tea_report['liquid_object_count']==1 and liquid.users_collection[0]==near.users_collection[0],
 'tea_center_is_horizontal':tea_report['flat_surface_height_range']<1e-6,
 'meniscus_is_submillimetre':.0007<tea_report['meniscus_rise_m']<.0009,
 'tea_is_below_the_rim':.014<tea_report['liquid_below_rim_m']<.016,
 'tea_base_does_not_penetrate_cup':0<=tea_report['liquid_floor_clearance_m']<.0003,
 'cup_and_plate_bodies_do_not_overlap':all(gap>.003 for gap in spacing.values()),
 'spout_has_real_wall_and_open_mouth':.0013<spout_report['mouth_wall_thickness_m']<.0015 and spout_report['center_ray_passes_open_lip'],
 'packed_reference_matches_original_bytes':packed_bytes==reference,
 'no_reference_or_other_image_projection':not textures,
 'relative_image_and_output_paths':not absolute_paths and not packed_absolute_paths and scene.render.filepath.startswith('//'),
 'no_private_machine_paths_in_saved_blend':b'/workspace/' not in blend_bytes and b'/home/' not in blend_bytes,
 'no_linked_external_blender_libraries':not bpy.data.libraries,
 'cpu_two_threads':scene.cycles.device=='CPU' and scene.render.threads_mode=='FIXED' and scene.render.threads==2,
}
report={'inspected_file':Path(bpy.data.filepath).name,'blender_version':bpy.app.version_string,
 'mesh_objects':len(records),'evaluated_vertices':sum(r['vertices'] for r in records),
 'contacts_to_table_m':contacts,'cup_geometry_raycast_tests':cups,'cup_handle_intrusion_depth_m':handle_intrusions,'tea_geometry':tea_report,'spout_geometry':spout_report,
 'circular_body_clearances_m':spacing,'reference_sha256':hashlib.sha256(reference).hexdigest(),
 'checks':checks,'all_assertions_pass':all(checks.values()),
 'render':{'engine':scene.render.engine,'device':scene.cycles.device,'threads':scene.render.threads,'samples':scene.cycles.samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'output':scene.render.filepath,'denoising':scene.cycles.use_denoising},
 'limitations':['Not a manufacturing, food-contact, heat, load or safety assessment.','Cup handles and kettle hardware have intentional hidden assembly overlaps.','Circular-body spacing is not exhaustive mesh/mesh collision certification.','Spout wall is closed and its bore is modeled; the boolean socket is not a fluid-tight or pouring validation.','Liquid has a 0.15 mm numerical floor clearance; meniscus is modeled, not simulated.','Liquid shadow rays and reflective/refractive caustics are disabled: an artistic optical approximation.','All reference image bytes are preserved; the scene uses no image texture nodes.'],
 'meshes':records}
path=ROOT/('work/draft_audit.json' if 'Draft' in Path(bpy.data.filepath).name else 'geometry_audit.json')
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('inspected_file','contacts_to_table_m','cup_geometry_raycast_tests','tea_geometry','checks','all_assertions_pass')},ensure_ascii=False,indent=2))
assert report['all_assertions_pass'],'Geometry audit failed; see report.'
