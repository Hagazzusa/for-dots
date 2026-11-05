"""Read-only, stdlib verification of the final frozen film bundle."""
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
manifest=json.loads((ROOT/"manifest.json").read_text())
for entry in manifest["files"]:
    p=Path(entry["path"])
    assert not p.is_absolute() and ".." not in p.parts and p.parts[0]!="work"
    data=(ROOT/p).read_bytes()
    assert len(data)==entry["size_bytes"] and sha(data)==entry["sha256"],p
source_manifest=json.loads((ROOT/"source_manifest.json").read_text())
for entry in source_manifest["files"]:
    data=(ROOT/entry["path"]).read_bytes()
    assert len(data)==entry["size_bytes"] and sha(data)==entry["sha256"]
audit=json.loads((ROOT/"qa/animation_audit.json").read_text())
assert audit["all_checks_pass"] and all(audit["checks"].values())
assert audit["animation_blend_sha256"]==sha((ROOT/"The_Second_Cup_Film.blend").read_bytes())
assert audit["source_blend_sha256"]=="eac50adac6aa30158ea9cfac70d9d3c71ae25602abc33975fb0ec2023c9f49bd"
assert audit["actual_saved_camera_minimum_hero_margin"]>.025
assert audit["actual_projection_max_difference_from_plan"]<1e-6
for source in (ROOT.parent/"second-cup/The_Second_Cup.blend",ROOT.parent/"second_cup/The_Second_Cup.blend"):
    if source.exists():assert sha(source.read_bytes())==audit["source_blend_sha256"]
checks=json.loads((ROOT/"qa/film_checks.json").read_text())
video=(ROOT/checks["video"]).read_bytes()
assert sha(video)==checks["video_sha256"] and len(video)==checks["video_bytes"]
assert checks["frame_count"]==72 and checks["fps"]==12 and checks["duration_seconds"]==6
assert checks["silent"] and checks["audio_streams"]==0
assert checks["full_decode_pass"] and checks["faststart_moov_before_mdat"] and checks["all_72_render_hashes_verified"]
assert len(checks["render_frame_records"])==72
for rec in checks["public_stills"]:
    data=(ROOT/rec["file"]).read_bytes();assert sha(data)==rec["public_sha256"]
    assert data[:8]==b"\x89PNG\r\n\x1a\n"
    at=8;compressed=[];dimensions=None
    while at<len(data):
        size=struct.unpack_from(">I",data,at)[0];kind=data[at+4:at+8];payload=data[at+8:at+8+size]
        assert zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from(">I",data,at+8+size)[0]
        if kind==b"IHDR":dimensions=list(struct.unpack_from(">II",payload))
        if kind==b"IDAT":compressed.append(payload)
        if kind in (b"tEXt",b"iTXt",b"zTXt"):assert payload.split(b"\0",1)[0]==b"Software"
        at+=size+12
    assert at==len(data) and dimensions==rec["dimensions"]
    assert sha(b"".join(compressed))==rec["idat_sha256"] and rec["idat_unchanged"] and rec["rgb_pixels_unchanged"]
provenance=json.loads((ROOT/"provenance.json").read_text())
assert sha((ROOT/"reference/gpt_image_concept.png").read_bytes())==provenance["concept_reference_sha256"]
native=json.loads((ROOT/"qa/native_playback.json").read_text())
assert native["video_sha256"]==checks["video_sha256"]
assert native["review_status"]=="completed"
assert native["accepted"] is True
print(json.dumps({"status":"pass","manifest_files":len(manifest["files"]),"video_seconds":6,"frames":72,"fps":12,
 "audio_streams":0,"all_saved_camera_frames_inside_margin":True,"source_sha_preserved":True,
 "video_sha256":checks["video_sha256"],"scope":"Stored evidence/hash verification; not a new render or native playback."},indent=2))
