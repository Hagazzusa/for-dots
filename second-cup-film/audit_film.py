"""Read-only saved-animation audit. Writes qa/animation_audit.json only."""
import argparse
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scene_fingerprint import fingerprint
parser=argparse.ArgumentParser()
source_candidates=[ROOT.parent/"second-cup/The_Second_Cup.blend",ROOT.parent/"second_cup/The_Second_Cup.blend"]
parser.add_argument("--source",type=Path,default=next((p for p in source_candidates if p.exists()),source_candidates[0]))
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
expected="eac50adac6aa30158ea9cfac70d9d3c71ae25602abc33975fb0ec2023c9f49bd"
source=args.source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source))
original=fingerprint()
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
for frame in (1,36,72):
    scene.frame_set(frame)
    all_same=all_same and fingerprint()==original
for frame in range(1,73):
    scene.frame_set(frame)
    positions.append(camera.location.copy())
    focus.append(camera.data.dof.focus_distance)
    assert camera.data.lens==80.0 and camera.data.dof.aperture_fstop==2.0
steps=[(b-a).length for a,b in zip(positions,positions[1:])]
accels=[(positions[i+1]-2*positions[i]+positions[i-1]).length for i in range(1,71)]
non_camera_animation=[ob.name for ob in scene.objects if ob!=camera and ob.animation_data]
animated_materials=[m.name for m in bpy.data.materials if m.animation_data or (m.node_tree and m.node_tree.animation_data)]
source_hash_after=hashlib.sha256(source.read_bytes()).hexdigest()
blend_bytes=film.read_bytes()
checks={"original_source_hash_unchanged":source_hash_after==expected,
 "saved_static_scene_matches_source":all_same,"no_non_camera_object_animation":not non_camera_animation,
 "no_material_animation":not animated_materials,
 "only_camera_animation_channels":set(f.data_path for f in camera.animation_data.action.fcurves)=={"location","rotation_quaternion"},
 "only_camera_data_focus_animation":set(f.data_path for f in camera.data.animation_data.action.fcurves)=={"dof.focus_distance"},
 "no_camera_constraints":len(camera.constraints)==0,
 "camera_smooth_small_steps":max(steps)<.004 and max(accels)<.0003,
 "five_original_prop_groups":scene.get("hero_prop_count")==5,
 "all_hero_bounds_inside_safe_frame":all(min(r["bounds_normalized_xy"][0],r["bounds_normalized_xy"][1],1-r["bounds_normalized_xy"][2],1-r["bounds_normalized_xy"][3])>.025 for f in plan["framing_all_frames"] for r in f["objects"]),
 "six_second_frame_range":scene.frame_start==1 and scene.frame_end==72 and scene.render.fps==12 and scene.render.fps_base==1,
 "cpu_two_threads":scene.cycles.device=="CPU" and scene.render.threads==2 and scene.render.threads_mode=="FIXED",
 "no_private_machine_paths_in_blend":b"/workspace/" not in blend_bytes and b"/home/" not in blend_bytes,
 "relative_render_path":scene.render.filepath.startswith("//"),
 "no_external_linked_blender_libraries":not bpy.data.libraries}
report={"blender_version":bpy.app.version_string,"source_blend_sha256":expected,
 "animation_blend_sha256":hashlib.sha256(blend_bytes).hexdigest(),
 "static_scene_sha256":original["static_scene_sha256"],"checks":checks,"all_checks_pass":all(checks.values()),
 "camera_travel_m":sum(steps),"maximum_step_m_per_frame":max(steps),"maximum_second_difference_m":max(accels),
 "focus_distance_start_end_m":[focus[0],focus[-1]],
 "frame_count":72,"fps":12,"duration_seconds":6,
 "geometry_scope":"Original evaluated mesh coordinates/topology, transforms, material assignments, node graphs, world and lights are fingerprinted. Camera/render settings intentionally differ.",
 "limitations":["Frame margins prove no hero vertex is cropped, not absence of all inter-object occlusion.","No fluid, heat, steam or pouring animation.","Original artistic liquid-shadow/caustic approximations remain unchanged."]}
(ROOT/"qa/animation_audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(report,indent=2,ensure_ascii=False))
assert report["all_checks_pass"],"Animation audit failed"
