import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parent
cfg=json.loads((P/'build-config.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'Eight-Spaces.blend'))
s=bpy.context.scene
assert s.render.resolution_x==cfg['resolution'] and s.cycles.samples==cfg['samples']
out=P/('probe.png' if cfg['mode']=='probe' else 'Eight-Spaces.png');s.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
raw=out.read_bytes();clean=bytearray(raw[:8]);at=8
while at<len(raw):
 size=int.from_bytes(raw[at:at+4],'big');kind=raw[at+4:at+8]
 if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:clean.extend(raw[at:at+size+12])
 at+=size+12
out.write_bytes(clean);print('Rendered',out)
