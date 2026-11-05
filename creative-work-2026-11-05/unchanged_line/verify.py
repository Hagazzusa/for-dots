from pathlib import Path
from pypdf import PdfReader
from PIL import Image,ImageChops
import json,hashlib
p=Path(__file__).resolve().parent
f=p/'output/pdf/Outside-One-Line.pdf';reader=PdfReader(f);assert len(reader.pages)==5
block='.647059 .305882 .223529 RG\n2.2 w\n1 J\n1 j\nn 90 300 m 170 300 l 210 345 l 270 345 l 310 300 l 390 300 l\nS'
for page in reader.pages:
 s=page.get_contents().get_data().decode()
 assert s.count(block)==1
 assert s.count(' cm')==1 # Only the identity transform established by ReportLab.
 assert list(page.mediabox)==[0,0,480,600]
first=Image.open(p/'tmp/pdfs/final-1.png').convert('RGB');last=Image.open(p/'tmp/pdfs/final-5.png').convert('RGB')
# Include header, drawing and surrounding whitespace, excluding captions and page number.
area=(0,0,first.width,round(first.height*420/600))
assert ImageChops.difference(first.crop(area),last.crop(area)).getbbox() is None
texts=[x.extract_text() for x in reader.pages]
assert '먼저 한 줄.' in texts[0] and '나머지를 지웠다.' in texts[-1]
q={'pages':5,'page_points':[480,600],'identical_target_path_style_in_all_pdf_streams':True,'identity_transform_only':True,'first_last_upper_70_percent_pixel_identical':True,'korean_text_extracts':True,'visual_review':'All five final rendered pages inspected: no clipping, missing glyphs or unintended overlaps. Intended transit connections and graph crossings remain behind the target line.','limitations':['Not a scientific perceptual study; no claim that every reader experiences the intended change.','PDF is not tagged PDF/UA. Text is extractable; a separate plain-text visual description is retained.','Fictional network and invented unitless graph, not travel information or measured data.'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(p/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False))
