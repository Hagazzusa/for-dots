"""Read-only saved-animation audit. Writes qa/animation_audit.json only."""
import argparse
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scene_fingerprint import fingerprint, digest, value
parser=argparse.ArgumentParser()
source_candidates=[ROOT.parent/"second-cup/The_Second_Cup.blend",ROOT.parent/"second_cup/The_Second_Cup.blend"]
parser.add_argument("--source",type=Path,default=next((p for p in source_candidates if p.exists()),source_candidates[0]))
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
expected="eac50adac6aa30158ea9cfac70d9d3c71ae25602abc33975fb0ec2023c9f49bd"
source=args.source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source))
original=fingerprint()
def supplemental_nodes(scene):
    """Cover outputs and RNA pointer settings omitted by the live guard.

    This is deliberately bounded to the node types used by this artwork.
    Arbitrary nested node groups/curves are not claimed as supported.
    """
    allowed={"BSDF_PRINCIPLED","OUTPUT_MATERIAL","TEX_COORD","TEX_NOISE","BUMP","MAP_RANGE","VOLUME_ABSORPTION","BACKGROUND","OUTPUT_WORLD"}
    def pointer_settings(obj,depth=0):
        if obj is None:return None
        if isinstance(obj,bpy.types.ID):return {"type":obj.bl_rna.identifier,"name":obj.name}
        assert depth<10,"Unsupported deep/cyclic node setting"
        result={}
        for prop in obj.bl_rna.properties:
            key=prop.identifier
            if key=="rna_type":continue
            item=getattr(obj,key)
            if prop.type=="POINTER":result[key]=pointer_settings(item,depth+1)
            elif prop.type=="COLLECTION":result[key]=[pointer_settings(x,depth+1) for x in item]
            else:result[key]=value(item)
        return result
    mats={m.name:m for ob in scene.objects if hasattr(ob.data,"materials") for m in ob.data.materials if m}
    trees=[("material:"+m.name,m.node_tree) for m in mats.values() if m.node_tree]
    trees.append(("world:"+scene.world.name,scene.world.node_tree))
    trees.extend(("light:"+ob.name,ob.data.node_tree) for ob in scene.objects if ob.type=="LIGHT" and ob.data.node_tree)
    records=[];types=set()
    for owner,tree in sorted(trees,key=lambda x:x[0]):
        for node in sorted(tree.nodes,key=lambda n:n.name):
            types.add(node.type);assert node.type in allowed,"Unsupported node coverage: "+node.type
            pointers={p.identifier:pointer_settings(getattr(node,p.identifier)) for p in node.bl_rna.properties if p.type=="POINTER" and p.identifier!="rna_type"}
            outputs=[{"identifier":s.identifier,"default_value":value(s.default_value)} for s in node.outputs if hasattr(s,"default_value")]
            records.append({"owner":owner,"node":node.name,"type":node.type,"pointers":pointers,"outputs":outputs})
    return {"sha256":digest(records),"node_types":sorted(types),"scope":"Output defaults and RNA pointer settings for this explicit node whitelist; not a general nested-group/curve auditor."}
original_node_supplement=supplemental_nodes(bpy.context.scene)
def evaluated_normals(scene):
    deps=bpy.context.evaluated_depsgraph_get();records=[]
    for ob in sorted(scene.objects,key=lambda o:o.name):
        if ob.type!="MESH":continue
        evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh()
        assert len(mesh.corner_normals)==len(mesh.loops),"Missing evaluated corner normals"
        records.append({"name":ob.name,"corner_normals":[list(n.vector) for n in mesh.corner_normals]})
        evaluated.to_mesh_clear()
    return digest(records)
original_normals=evaluated_normals(bpy.context.scene)
def optical_settings(scene):
    return {"view":{k:getattr(scene.view_settings,k) for k in ("view_transform","look","exposure","gamma")},
      "cycles":{k:getattr(scene.cycles,k) for k in ("max_bounces","diffuse_bounces","glossy_bounces","transmission_bounces","caustics_reflective","caustics_refractive","sample_clamp_direct","sample_clamp_indirect")},
      "world":scene.world.name,"film_transparent":scene.render.film_transparent,"display_device":scene.display_settings.display_device,
      "compositor_enabled":scene.use_nodes}
original_optics=optical_settings(bpy.context.scene)
film=ROOT/"The_Second_Cup_Film.blend"
bpy.ops.wm.open_mainfile(filepath=str(film))
scene=bpy.context.scene;camera=scene.camera
plan=json.loads((ROOT/"camera_plan.json").read_text())
scene.frame_set(1)
saved=fingerprint()
if not saved==original==plan["static_scene_fingerprint"]:
    (ROOT/"work/fingerprint_debug.json").write_text(json.dumps({"original":original,"saved":saved,"plan":plan["static_scene_fingerprint"]},indent=2))
assert saved==original==plan["static_scene_fingerprint"]
all_same=True
positions=[];focus=[]
focus_max_error=0.0
deps=bpy.context.evaluated_depsgraph_get()
hero=[]
for ob in scene.objects:
    if ob.type=="MESH" and any(c.name[:2] in ("01","02","03","04","05") for c in ob.users_collection):
        evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh()
        hero.append((ob.name,[ob.matrix_world@v.co for v in mesh.vertices]))
        evaluated.to_mesh_clear()
actual_framing=[]
for frame in (1,36,72):
    scene.frame_set(frame)
    all_same=all_same and fingerprint()==original
for frame in range(1,73):
    scene.frame_set(frame)
    positions.append(camera.location.copy())
    focus.append(camera.data.dof.focus_distance)
    assert camera.data.lens==80.0 and camera.data.dof.aperture_fstop==2.0
    assert camera.data.dof.use_dof and camera.data.dof.focus_object is None
    focus_max_error=max(focus_max_error,abs(camera.data.dof.focus_distance-plan["camera_frames"][frame-1]["focus_distance"]))
    bounds=[]
    for name,vertices in hero:
        projected=[world_to_camera_view(scene,camera,v) for v in vertices]
        assert min(v.z for v in projected)>0
        box=[min(v.x for v in projected),min(v.y for v in projected),max(v.x for v in projected),max(v.y for v in projected)]
        bounds.append({"name":name,"bounds_normalized_xy":box})
    actual_framing.append({"frame":frame,"objects":bounds})
steps=[(b-a).length for a,b in zip(positions,positions[1:])]
accels=[(positions[i+1]-2*positions[i]+positions[i-1]).length for i in range(1,71)]
non_camera_animation=[ob.name for ob in scene.objects if ob!=camera and ob.animation_data]
animated_materials=[m.name for m in bpy.data.materials if m.animation_data or (m.node_tree and m.node_tree.animation_data)]
source_hash_after=hashlib.sha256(source.read_bytes()).hexdigest()
blend_bytes=film.read_bytes()
image_paths=[{"name":im.name,"path":im.filepath,"packed":bool(im.packed_file),
              "packed_paths":[pf.filepath for pf in im.packed_files]} for im in bpy.data.images if im.source=="FILE"]
browser_paths=[]
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=="FILE_BROWSER" and space.params:
                browser_paths.append(bytes(space.params.directory).decode("utf-8","replace"))
drivers=[]
owners=list(bpy.data.objects)+list(bpy.data.materials)+list(bpy.data.cameras)+list(bpy.data.lights)+list(bpy.data.worlds)+list(bpy.data.scenes)+list(bpy.data.node_groups)
owners += list(bpy.data.meshes)+list(bpy.data.shape_keys)
owners += [m.node_tree for m in bpy.data.materials if m.node_tree]
owners += [w.node_tree for w in bpy.data.worlds if w.node_tree]
for owner in owners:
    animation=getattr(owner,"animation_data",None)
    if animation:
        drivers.extend({"owner":owner.name,"path":curve.data_path} for curve in animation.drivers)
actual_margin=min(min(r["bounds_normalized_xy"][0],r["bounds_normalized_xy"][1],1-r["bounds_normalized_xy"][2],1-r["bounds_normalized_xy"][3]) for f in actual_framing for r in f["objects"])
plan_delta=0.0
for expected_frame,actual_frame in zip(plan["framing_all_frames"],actual_framing):
    expected_objects={o["name"]:o["bounds_normalized_xy"] for o in expected_frame["objects"]}
    actual_objects={o["name"]:o["bounds_normalized_xy"] for o in actual_frame["objects"]}
    assert expected_objects.keys()==actual_objects.keys()
    plan_delta=max(plan_delta,max(abs(a-b) for name in expected_objects for a,b in zip(expected_objects[name],actual_objects[name])))
checks={"original_source_hash_unchanged":source_hash_after==expected,
 "saved_static_scene_matches_source":all_same,"no_non_camera_object_animation":not non_camera_animation,
 "original_optical_and_color_settings_preserved":optical_settings(scene)==original_optics,
 "bounded_node_pointer_and_output_comparison":supplemental_nodes(scene)==original_node_supplement,
 "evaluated_corner_normals_match_source":evaluated_normals(scene)==original_normals,
 "no_material_animation":not animated_materials,
 "only_camera_animation_channels":set(f.data_path for f in camera.animation_data.action.fcurves)=={"location","rotation_quaternion"},
 "only_camera_data_focus_animation":set(f.data_path for f in camera.data.animation_data.action.fcurves)=={"dof.focus_distance"},
 "saved_focus_curve_matches_all_72_planned_frames":focus_max_error<1e-6,
 "dof_active_without_focus_object_override":camera.data.dof.use_dof and camera.data.dof.focus_object is None,
 "no_camera_constraints":len(camera.constraints)==0,
 "camera_smooth_small_steps":max(steps)<.004 and max(accels)<.0003,
 "five_original_prop_groups":scene.get("hero_prop_count")==5,
 "saved_camera_all_hero_bounds_inside_safe_frame":actual_margin>.025,
 "saved_camera_projection_matches_plan":plan_delta<1e-6,
 "six_second_frame_range":scene.frame_start==1 and scene.frame_end==72 and scene.render.fps==12 and scene.render.fps_base==1,
 "cpu_two_threads":scene.cycles.device=="CPU" and scene.render.threads==2 and scene.render.threads_mode=="FIXED",
 "no_private_machine_paths_in_blend":b"/workspace/" not in blend_bytes and b"/home/" not in blend_bytes,
 "blend_storage_is_uncompressed":blend_bytes.startswith(b"BLENDER"),
 "native_image_and_packed_paths_relative":all(i["path"].startswith("//") and i["packed"] and all(p.startswith("//") or not Path(p).is_absolute() for p in i["packed_paths"]) for i in image_paths),
 "native_browser_paths_safe":all(p in ("","//") for p in browser_paths),
 "no_drivers":not drivers,
 "no_embedded_python_texts":not bpy.data.texts,
 "relative_render_path":scene.render.filepath.startswith("//"),
 "no_external_linked_blender_libraries":not bpy.data.libraries}
report={"blender_version":bpy.app.version_string,"source_blend_sha256":expected,
 "animation_blend_sha256":hashlib.sha256(blend_bytes).hexdigest(),
 "static_scene_sha256":original["static_scene_sha256"],"checks":checks,"all_checks_pass":all(checks.values()),
 "camera_travel_m":sum(steps),"maximum_step_m_per_frame":max(steps),"maximum_second_difference_m":max(accels),
 "focus_distance_start_end_m":[focus[0],focus[-1]],
 "maximum_focus_distance_difference_from_plan_m":focus_max_error,
 "actual_saved_camera_minimum_hero_margin":actual_margin,
 "actual_projection_max_difference_from_plan":plan_delta,
 "projection_method":"Reopened saved animation; evaluated hero vertices projected through actual saved camera at every integer frame 1..72. Not a re-check of plan bounds alone.",
 "native_metadata":{"image_paths":image_paths,"file_browser_directories":browser_paths,"render_path":scene.render.filepath,"drivers":drivers,"external_libraries":[]},
 "preserved_optical_settings":original_optics,
 "supplemental_node_audit":original_node_supplement,
 "evaluated_corner_normals_sha256":original_normals,
 "frame_count":72,"fps":12,"duration_seconds":6,
 "geometry_scope":"This scene's evaluated mesh coordinates/topology, transforms, material assignments and recorded node properties/world/lights are fingerprinted. Separate bounded checks compare evaluated corner normals and the used node types' output/pointer values. Not a general arbitrary Blender node-group auditor. Camera/render settings intentionally differ.",
 "limitations":["Frame margins prove no hero vertex is cropped, not absence of all inter-object occlusion.","No fluid, heat, steam or pouring animation.","Original artistic liquid-shadow/caustic approximations remain unchanged."]}
(ROOT/"qa/animation_audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(report,indent=2,ensure_ascii=False))
assert report["all_checks_pass"],"Animation audit failed"
