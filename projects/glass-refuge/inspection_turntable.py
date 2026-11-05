"""Geometry-only Workbench orbit. Does not save or change the delivery .blend.
Glazing, landscape and light fixtures are hidden only for this inspection output.
"""
import bpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent;out=root/'renders'/'inspection_frames';out.mkdir(exist_ok=True)
s=bpy.context.scene
for c in bpy.data.collections:
 if c.name.startswith(('03 |','08 |','09 |')):
  for o in c.objects:o.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=480;s.render.resolution_y=480;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=2
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.08,.09,.11)
s.camera.data.lens=45
for frame in range(24):
 a=-math.pi/2+math.pi*2*frame/24
 s.camera.location=(8*math.cos(a),8*math.sin(a),4.5)
 s.camera.rotation_euler=(Vector((0,0,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(out/f'{frame:03}.png');bpy.ops.render.render(write_still=True)
print('INSPECTION_RENDERED_24_FRAMES')
