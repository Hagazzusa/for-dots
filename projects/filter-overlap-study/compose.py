"""Create a labeled contact sheet from measured render previews (not recolored)."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent
report=json.loads((root/'measurements.json').read_text())
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try:
 title=ImageFont.truetype(font_path,30); head=ImageFont.truetype(font_path,18); small=ImageFont.truetype(font_path,14)
except OSError: title=head=small=ImageFont.load_default()
canvas=Image.new('RGB',(1000,925),'#f3f0e8'); d=ImageDraw.Draw(canvas)
d.text((35,24),'When two filters overlap',font=title,fill='#273b39'); d.text((35,67),'A controlled RGB light study / actual Cycles floor renders',font=head,fill='#536461')
labels=['No filter / control','Cyan only','Yellow only','Both / pure transmission','Both / gallery shader','Gallery / direct light only']
for i,(row,label) in enumerate(zip(report['cases'],labels)):
 x=35+(i%3)*325; y=115+(i//3)*345
 d.text((x,y),label,font=head,fill='#273b39'); im=Image.open(root/(row['case']+'.png')).convert('RGB'); canvas.paste(im,(x,y+34))
 rgb=row['normalized_to_control']; d.text((x,y+300),'RGB  '+', '.join(f'{v:.4f}' for v in rgb),font=small,fill='#273b39')
d.text((35,822),'Ratios use the same central 32 x 32 patch in 32-bit linear EXR, divided by control.',font=small,fill='#273b39')
d.text((35,847),'Preview: Standard / sRGB. Measurement: scene-linear Rec.709. Exposure 0; gamma 1.',font=small,fill='#536461')
d.text((35,872),'Thin RGB filters, not spectral glass. Filters hidden from camera rays only; shadows remain active.',font=small,fill='#536461')
canvas.save(root/'Filter-Overlap-Comparison.png')
