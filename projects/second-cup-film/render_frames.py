"""Serial, resumable Cycles frame render. Runs inside Blender, CPU 2 threads.

blender -b -t 2 --python-exit-code 1 --python render_frames.py
Only verified complete PNGs whose journal hashes match are skipped.
"""
import bpy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import zlib

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scene_fingerprint import fingerprint
FRAMES=ROOT/"work/frames";FRAMES.mkdir(parents=True,exist_ok=True)
JOURNAL=ROOT/"work/render_progress.json"
film=ROOT/"The_Second_Cup_Film.blend"
film_sha=hashlib.sha256(film.read_bytes()).hexdigest()
plan=json.loads((ROOT/"camera_plan.json").read_text())
audit=json.loads((ROOT/"qa/animation_audit.json").read_text())
assert audit["all_checks_pass"] and audit["animation_blend_sha256"]==film_sha
bpy.ops.wm.open_mainfile(filepath=str(film))
scene=bpy.context.scene
assert scene.render.resolution_x==scene.render.resolution_y==768
assert scene.cycles.samples==64 and scene.render.threads==2 and scene.cycles.device=="CPU"
assert fingerprint()==plan["static_scene_fingerprint"]

def utc():return datetime.now(timezone.utc).isoformat()
def save_progress(state):
    p=JOURNAL.with_suffix(".pending.json")
    p.write_text(json.dumps(state,indent=2)+"\n");p.replace(JOURNAL)
def png_complete(path):
    data=path.read_bytes();assert data[:8]==b"\x89PNG\r\n\x1a\n"
    at=8;compressed=[];dims=None;last=None
    while at<len(data):
        n=struct.unpack_from(">I",data,at)[0];kind=data[at+4:at+8];payload=data[at+8:at+8+n]
        assert len(payload)==n
        assert zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from(">I",data,at+8+n)[0]
        if kind==b"IHDR":dims=struct.unpack_from(">II",payload)
        if kind==b"IDAT":compressed.append(payload)
        at+=n+12;last=kind
    assert at==len(data) and last==b"IEND" and dims==(768,768)
    assert zlib.decompress(b"".join(compressed))
    return hashlib.sha256(data).hexdigest()

if JOURNAL.exists():
    state=json.loads(JOURNAL.read_text())
    assert state["animation_blend_sha256"]==film_sha,"Cannot mix frames from a different animation"
else:
    state={"animation_blend_sha256":film_sha,"started_utc":utc(),"frames":{},"status":"running",
      "resolution":[768,768],"samples":64,"threads":2,"expected_frames":72}
for frame in range(1,73):
    destination=FRAMES/("frame_%04d.png"%frame)
    record=state["frames"].get(str(frame))
    if record and destination.exists():
        assert png_complete(destination)==record["sha256"],"Completed frame hash changed"
        print("FILM_FRAME_VERIFIED_SKIP",frame,flush=True);continue
    assert not destination.exists(),"Unjournaled frame exists; preserve/review it before resuming"
    scene.frame_set(frame)
    assert fingerprint()==plan["static_scene_fingerprint"],"Static scene changed"
    state.update(status="running",current_frame=frame,updated_utc=utc())
    save_progress(state)
    scene.render.filepath="//work/frames/frame_%04d.pending.png"%frame
    pending=FRAMES/("frame_%04d.pending.png"%frame)
    started=time.monotonic()
    bpy.ops.render.render(write_still=True)
    seconds=time.monotonic()-started
    sha=png_complete(pending)
    pending.replace(destination)
    state["frames"][str(frame)]={"file":destination.name,"sha256":sha,"seconds":seconds,"size_bytes":destination.stat().st_size}
    state.update(completed_frames=len(state["frames"]),updated_utc=utc())
    save_progress(state)
    print("FILM_FRAME_DONE",frame,"of 72",round(seconds,2),"seconds",flush=True)
state.update(status="complete",completed_utc=utc(),current_frame=None)
save_progress(state)
print("SECOND_CUP_FILM_RENDER_COMPLETE",flush=True)
