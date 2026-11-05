import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parent;(R/'work').mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'LL.blend'));s=bpy.context.scene;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=2;s.view_settings.gamma=1;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
spaces={}
for case in ['LL','HL','LH','HH','LL_repeat','HH_repeat']:
 im=bpy.data.images.load(str(R/'renders'/f'{case}.exr'),check_existing=False);spaces[case]=im.colorspace_settings.name;im.save_render(str(R/'work'/f'{case}_from_exr.png'),scene=s)
(R/'records/exr_color_spaces.json').write_text(json.dumps(spaces,indent=2)+'\n')
