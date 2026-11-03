import bpy,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent
shutil.copy2(R/'renders/LL.png',R/'renders/preview_initial_exposure0.png')
bpy.ops.wm.open_mainfile(filepath=str(R/'LL.blend'));s=bpy.context.scene;s.view_settings.exposure=2
im=bpy.data.images.load(str(R/'renders/LL.exr'));s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';im.save_render(str(R/'renders/LL.png'),scene=s);bpy.ops.wm.save_as_mainfile(filepath=str(R/'LL.blend'))
p=R/'records/LL.json';r=json.loads(p.read_text());r['view'][2]=2;r['preview_display_choice']='Before any other matrix case, selected fixed +2 display exposure for all PNGs. Initial exposure-0 PNG retained. Same scene-linear EXR and samples, no selective brightening.';p.write_text(json.dumps(r,indent=2)+'\n')
print(im.colorspace_settings.name)
