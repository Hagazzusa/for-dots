"""Derive a six-second camera/focus animation from the immutable source artwork.

blender -b -t 2 --python-exit-code 1 --python rebuild_film.py -- --draft
Only this folder is written. --source can locate an unchanged original .blend.
"""
import argparse
import bpy
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scene_fingerprint import fingerprint
SOURCE_SHA="eac50adac6aa30158ea9cfac70d9d3c71ae25602abc33975fb0ec2023c9f49bd"
parser=argparse.ArgumentParser()
source_candidates=[ROOT.parent/"second-cup/The_Second_Cup.blend",ROOT.parent/"second_cup/The_Second_Cup.blend"]
parser.add_argument("--source",type=Path,default=next((p for p in source_candidates if p.exists()),source_candidates[0]))
parser.add_argument("--draft",action="store_true")
parser.add_argument("--render",action="store_true",help="Render all 72 frames, serially.")
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
for name in ("work/tmp","qa","renders","reference"):(ROOT/name).mkdir(parents=True,exist_ok=True)
source=args.source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA,"Source artwork hash differs"
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
before=fingerprint()
camera=scene.camera
camera.animation_data_clear();camera.data.animation_data_clear()
camera.rotation_mode="QUATERNION"
camera.data.lens=80.0
camera.data.dof.use_dof=True
camera.data.dof.focus_object=None
camera.data.dof.aperture_fstop=2.0
camera.data.dof.aperture_blades=7
camera.data.dof.aperture_ratio=1.0
scene.frame_start=1;scene.frame_end=72;scene.render.fps=12;scene.render.fps_base=1.0
start=Vector((.075,-1.12,1.18));end=Vector((.170,-1.06,1.17))
aim_start=Vector((-.025,-.005,.040));aim_end=Vector((.015,.020,.045))
near=Vector((-.170,-.165,.059));far=Vector((.155,.120,.030))

def ease(t):
    t=min(1.0,max(0.0,t))
    return t*t*t*(t*(t*6.0-15.0)+10.0)

camera_records=[]
for frame in range(1,73):
    t=ease((frame-1)/71)
    camera.location=start.lerp(end,t)
    aim=aim_start.lerp(aim_end,t)
    direction=(aim-camera.location).normalized()
    camera.rotation_quaternion=direction.to_track_quat("-Z","Y")
    focus_mix=ease((frame-12)/48)
    focus_point=near.lerp(far,focus_mix)
    camera.data.dof.focus_distance=(focus_point-camera.location).dot(direction)
    camera.keyframe_insert("location",frame=frame)
    camera.keyframe_insert("rotation_quaternion",frame=frame)
    camera.data.dof.keyframe_insert("focus_distance",frame=frame)
    camera_records.append({"frame":frame,"seconds":(frame-1)/12,"location":list(camera.location),
        "aim":list(aim),"focus_point":list(focus_point),"focus_mix":focus_mix,
        "focus_distance":camera.data.dof.focus_distance})
for owner in (camera,camera.data):
    for curve in owner.animation_data.action.fcurves:
        for key in curve.keyframe_points:key.interpolation="LINEAR"

scene.render.engine="CYCLES";scene.cycles.device="CPU"
scene.render.threads_mode="FIXED";scene.render.threads=2
scene.cycles.samples=64
scene.cycles.use_denoising=False
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.025
scene.cycles.seed=5;scene.cycles.use_animated_seed=False
scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGB"
scene.render.image_settings.color_depth="8";scene.render.use_stamp=False
scene.render.use_motion_blur=False
scene.render.filepath="//work/frames/frame_"
scene.render.use_file_extension=True
scene["film_title"]="두 잔의 자리 · 눈길이 머무는 곳"
scene["film_note"]="Silent 6-second camera and focus study; original geometry, materials, lights, liquid height and fictional story unchanged."
scene["film_source_sha256"]=SOURCE_SHA
scene["film_camera_only"]=True

# Keep the packed concept bytes intact and retain a project-relative fallback.
for im in bpy.data.images:
    if im.packed_file:
        data=bytes(im.packed_file.data)
        assert im.filepath=="//reference/gpt_image_concept.png"
        (ROOT/"reference/gpt_image_concept.png").write_bytes(data)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":area.spaces.active.region_3d.view_perspective="CAMERA"
        for space in area.spaces:
            if space.type=="FILE_BROWSER" and space.params:
                space.params.directory=b"/"*1023;space.params.directory=b"//"
                space.params.filename="_"*255;space.params.filename=""

scene.frame_set(1)
after=fingerprint()
assert before==after,"Static scene changed while building animation"

# Project every evaluated hero vertex, not just a center or approximate sphere.
hero=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in scene.objects:
    if ob.type=="MESH" and any(c.name[:2] in ("01","02","03","04","05") for c in ob.users_collection):
        evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh()
        hero.append((ob.name,[ob.matrix_world@v.co for v in mesh.vertices]))
        evaluated.to_mesh_clear()
framing=[]
for frame in range(1,73):
    scene.frame_set(frame)
    per_object=[]
    for name,points in hero:
        p=[world_to_camera_view(scene,camera,v) for v in points]
        bounds=[min(v.x for v in p),min(v.y for v in p),max(v.x for v in p),max(v.y for v in p)]
        assert min(v.z for v in p)>0
        assert min(bounds[0],bounds[1],1-bounds[2],1-bounds[3])>.025,(frame,name,bounds)
        per_object.append({"name":name,"bounds_normalized_xy":bounds})
    framing.append({"frame":frame,"objects":per_object})
scene.frame_set(1)
filename=ROOT/"The_Second_Cup_Film.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(filename),relative_remap=False)
assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
plan={"title":scene["film_title"],"source_sha256":SOURCE_SHA,"static_scene_fingerprint":before,
 "static_scene_unchanged":True,"camera_frames":camera_records,"framing_all_frames":framing,
 "frame_count":72,"fps":12,"duration_seconds":6.0,"silent":True,"lens_mm":80,"fstop":2.0,
 "camera_travel_m":(end-start).length,"minimum_hero_frame_margin":.025,
 "render":{"resolution":[768,768],"samples":64,"threads":2,"device":"CPU","denoising":False},
 "source_geometry_materials_lights_and_world_preserved":True}
(ROOT/"camera_plan.json").write_text(json.dumps(plan,indent=2,ensure_ascii=False)+"\n")
if args.draft:
    scene.render.resolution_x=480;scene.render.resolution_y=480
    scene.cycles.samples=24;scene.cycles.adaptive_threshold=.05
    timings=[]
    for frame in (1,36,72):
        scene.frame_set(frame);scene.render.filepath="//work/draft_%03d.png"%frame
        t=time.monotonic();bpy.ops.render.render(write_still=True)
        timings.append({"frame":frame,"seconds":time.monotonic()-t})
    (ROOT/"work/draft_timings.json").write_text(json.dumps(timings,indent=2)+"\n")
elif args.render:
    (ROOT/"work/frames").mkdir(exist_ok=True)
    bpy.ops.render.render(animation=True)
print("SECOND_CUP_FILM_READY",filename.name)
