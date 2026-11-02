"""Assemble the completed silent film and safe stills; no scene/image retouching.

Run with normal Python (Pillow installed), after render_frames.py finishes.
FFmpeg with libx264 and zscale, plus ffprobe, are required.
"""
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import zlib
from PIL import Image

ROOT=Path(__file__).resolve().parent
VIDEO="renders/The_Second_Cup_Silent_Film.mp4"
FILTER="format=gbrp,zscale=matrixin=gbr:primariesin=bt709:transferin=iec61966-2-1:rangein=full:matrix=bt709:primaries=bt709:transfer=iec61966-2-1:range=limited,format=yuv420p"
RENDER_KEYS={"File","Date","Time","Frame","Camera","Scene","RenderTime","Memory","Samples","Marker","Hostname",
 "cycles.ViewLayer.samples","cycles.ViewLayer.total_time","cycles.ViewLayer.render_time","cycles.ViewLayer.synchronization_time"}

def sha(data):return hashlib.sha256(data).hexdigest()
def chunks(data):
    assert data[:8]==b"\x89PNG\r\n\x1a\n"
    at=8
    while at<len(data):
        size=struct.unpack_from(">I",data,at)[0];kind=data[at+4:at+8];payload=data[at+8:at+8+size];packet=data[at:at+12+size]
        assert len(packet)==size+12 and zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from(">I",packet,len(packet)-4)[0]
        yield kind,payload,packet
        at+=size+12
    assert at==len(data)
def idat(data):return b"".join(p for k,p,r in chunks(data) if k==b"IDAT")
def safe_still(source,destination):
    original=source.read_bytes();output=original[:8];removed=[]
    for kind,payload,packet in chunks(original):
        if kind in (b"tEXt",b"zTXt",b"iTXt"):
            key=payload.split(b"\0",1)[0].decode("latin1")
            if key!="Software":
                assert key in RENDER_KEYS,"Unexpected metadata; review rather than stripping: "+key
                removed.append(key);continue
        output+=packet
    a=Image.open(io.BytesIO(original)).convert("RGB");b=Image.open(io.BytesIO(output)).convert("RGB")
    assert a.size==b.size and a.tobytes()==b.tobytes() and idat(original)==idat(output)
    destination.parent.mkdir(exist_ok=True);destination.write_bytes(output)
    return {"file":destination.relative_to(ROOT).as_posix(),"raw_sha256":sha(original),"public_sha256":sha(output),
       "idat_sha256":sha(idat(output)),"rgb_sha256":sha(b.tobytes()),"dimensions":list(b.size),
       "removed_renderer_text_keys":removed,"idat_unchanged":True,"rgb_pixels_unchanged":True}
def run(arguments,log):
    result=subprocess.run(arguments,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (ROOT/"work"/log).write_text(result.stdout)
    assert result.returncode==0,"Command failed; see work/"+log
    return result.stdout

progress=json.loads((ROOT/"work/render_progress.json").read_text())
assert progress["status"]=="complete" and len(progress["frames"])==72
assert progress["animation_blend_sha256"]==sha((ROOT/"The_Second_Cup_Film.blend").read_bytes())
for frame in range(1,73):
    path=ROOT/"work/frames"/("frame_%04d.png"%frame)
    assert sha(path.read_bytes())==progress["frames"][str(frame)]["sha256"]
    im=Image.open(path);assert im.size==(768,768);im.verify()
(ROOT/"renders").mkdir(exist_ok=True)
still_reports=[]
for frame in (1,36,72):
    draft=ROOT/"work"/("draft_%03d.png"%frame)
    if draft.exists():still_reports.append(safe_still(draft,ROOT/"qa"/("draft_%03d.png"%frame)))
    still_reports.append(safe_still(ROOT/"work/frames"/("frame_%04d.png"%frame),ROOT/"renders"/("frame_%04d.png"%frame)))

encode=["ffmpeg","-hide_banner","-y","-threads","2","-filter_threads","2","-framerate","12","-start_number","1",
 "-i","work/frames/frame_%04d.png","-frames:v","72","-an","-vf",FILTER,
 "-c:v","libx264","-threads","2","-preset","slow","-crf","18","-pix_fmt","yuv420p",
 "-color_primaries","bt709","-colorspace","bt709","-color_trc","iec61966-2-1","-color_range","tv",
 "-fps_mode","passthrough","-map_metadata","-1","-movflags","+faststart",
 "-metadata","title=The Second Cup - Silent Camera Study",VIDEO]
run(encode,"encode.log")
probe=json.loads(run(["ffprobe","-v","error","-count_frames","-show_entries",
 "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,nb_frames,nb_read_frames,color_range,color_space,color_transfer,color_primaries:format=duration,format_name,size:format_tags=title,encoder",
 "-of","json",VIDEO],"probe.json"))
video=[s for s in probe["streams"] if s["codec_type"]=="video"]
audio=[s for s in probe["streams"] if s["codec_type"]=="audio"]
assert len(video)==1 and not audio
v=video[0]
assert v["codec_name"]=="h264" and (v["width"],v["height"])==(768,768) and v["pix_fmt"]=="yuv420p"
assert v["avg_frame_rate"]==v["r_frame_rate"]=="12/1" and int(v["nb_read_frames"])==72
assert abs(float(probe["format"]["duration"])-6.0)<.001
assert v["color_space"]==v["color_primaries"]=="bt709" and v["color_transfer"]=="iec61966-2-1"
assert v["color_range"]=="tv"
run(["ffmpeg","-v","error","-threads","2","-i",VIDEO,"-f","null","-"],"decode_check.log")
data=(ROOT/VIDEO).read_bytes();atoms=[];at=0
while at<len(data):
    size,kind=struct.unpack_from(">I4s",data,at)
    if size==1:size=struct.unpack_from(">Q",data,at+8)[0]
    if size==0:size=len(data)-at
    assert size>=8 and at+size<=len(data)
    atoms.append(kind.decode("latin1"));at+=size
assert at==len(data) and atoms.index("moov")<atoms.index("mdat")
assert b"/workspace/" not in data and b"/home/" not in data
timings=[progress["frames"][str(i)]["seconds"] for i in range(1,73)]
report={"video":VIDEO,"video_sha256":sha(data),"video_bytes":len(data),"silent":True,"audio_streams":0,
 "frame_count":72,"fps":12,"duration_seconds":6,"resolution":[768,768],"probe":probe,
 "full_decode_pass":True,"faststart_moov_before_mdat":True,"all_72_render_hashes_verified":True,
 "render_seconds":{"total":sum(timings),"minimum":min(timings),"maximum":max(timings),"mean":sum(timings)/72},
 "render_frame_records":[{"frame":i,**progress["frames"][str(i)]} for i in range(1,73)],
 "public_stills":still_reports,"encoding_command_relative":encode,
 "color_pipeline":"Display-referred sRGB PNG; preserve sRGB transfer, convert RGB to limited-range BT.709 matrix YUV420p. H.264 explicitly tags BT.709 primaries/matrix and IEC 61966-2-1 transfer.",
 "encoding_is_lossy":True,"frame_interpolation_or_image_retouching":False,
 "native_playback_review":"pending; this file proves decode/format only, not visual playback quality"}
(ROOT/"qa/film_checks.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:report[k] for k in ("video","video_sha256","video_bytes","frame_count","duration_seconds","silent","full_decode_pass")},indent=2))
