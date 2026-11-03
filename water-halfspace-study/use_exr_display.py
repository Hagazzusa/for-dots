"""Use the same EXR-to-AgX export path for every display PNG. No rendering."""
from pathlib import Path
import shutil,json
R=Path(__file__).resolve().parent
for case in ['LL','HL','LH','HH','LL_repeat','HH_repeat']:
 p=R/'renders'/f'{case}.png';backup=R/'work'/f'{case}_direct_render.png'
 if not backup.exists():shutil.copy2(p,backup)
 shutil.copy2(R/'work'/f'{case}_from_exr.png',p)
(R/'records/display_pipeline.json').write_text(json.dumps({'canonical_PNGs':'All six PNGs use identical EXR -> Blender AgX Medium High Contrast, exposure +2, gamma 1 -> 8-bit RGB save_render.','direct_exports_preserved':'work/*_direct_render.png','comparison':'Direct render PNG versus EXR re-display differed by at most 2/255 per channel (LL identical). See png_exr_display_consistency.json. No ROI measurement uses PNG.','linear_inputs_unchanged':True,'additional_renders':0},indent=2)+'\n')
