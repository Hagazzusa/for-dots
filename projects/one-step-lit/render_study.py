"""Two lighting states for an original scene; only porch light changes between states."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise SystemExit('Pass the Last-Umbrella.blend source path after --')
source=Path(args[0]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;s.cycles.samples=32;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=650;s.render.resolution_y=650;s.render.resolution_percentage=100
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.08
bpy.data.objects['Cloudy dusk'].data.energy=65
bpy.data.objects['Soft side light'].data.energy=25
lamp=bpy.data.objects['Amber porch lamp']; material=bpy.data.materials['Milk glass warm light'];bs=material.node_tree.nodes['Principled BSDF']
# Exact same camera, mesh, materials and exposure in the pair. Time-of-day lighting
# differs from the earlier standalone still, but stays fixed throughout this study.
for name,power,emission in [('01-light-off.png',0,0),('02-light-on.png',55,3)]:
 lamp.data.energy=power;bs.inputs['Emission Strength'].default_value=emission
 s.render.filepath=str(ROOT/name);bpy.ops.render.render(write_still=True)
 p=ROOT/name;raw=p.read_bytes();out=bytearray(raw[:8]);off=8
 while off<len(raw):
  n=int.from_bytes(raw[off:off+4],'big');kind=raw[off+4:off+8]
  if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out.extend(raw[off:off+n+12])
  off+=n+12
 p.write_bytes(out)
(ROOT/'conditions.json').write_text(json.dumps({'blender':bpy.app.version_string,'resolution':[650,650],'samples':32,'camera_unchanged_between_states':True,'scene_geometry_unchanged':True,'off_lamp_power':0,'on_lamp_power':55,'off_emission':0,'on_emission':3,'ambient_strength':.08,'sky_power':65,'fill_power':25,'use':'storyboard lighting sketch, not a visibility/safety validation'},indent=2)+'\n')
