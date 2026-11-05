from pathlib import Path
import json,hashlib
import fitz
from PIL import Image
P=Path(__file__).resolve().parent
pdf=P/'output/pdf/While-Carrying.pdf';png=P/'While-Carrying.png';d=fitz.open(pdf);assert len(d)==1;p=d[0];assert tuple(p.rect)==(0,0,760,540);assert p.get_text()==''
shapes=p.get_drawings();frames=[v['rect'] for v in shapes if abs(v['rect'].width-350)<1e-4 and abs(v['rect'].height-240)<1e-4];assert len(frames)==4
assert all(any(f.contains(v['rect']) for f in frames) for v in shapes if v['rect']!=p.rect)
seats=[v['rect'] for v in shapes if abs(v['rect'].width-130)<1e-4 and abs(v['rect'].height-5)<1e-4];assert len(seats)==4
colors=[(77/255,113/255,128/255),(179/255,102/255,78/255)]
for frame in frames:
 for color in colors:
  assert any(frame.contains(v['rect']) and v['fill'] and max(abs(a-b) for a,b in zip(v['fill'],color))<1e-5 for v in shapes)
geometry=json.loads((P/'geometry.json').read_text());assert len(geometry)==4
for i,g in enumerate(geometry):
 ox,oy=g['origin'];expected=fitz.Rect(ox+g['bench_left'],540-oy-g['seat_base_y']-5,ox+g['bench_left']+130,540-oy-g['seat_base_y'])
 assert any(max(abs(a-b) for a,b in zip(expected,r))<1e-4 for r in seats)
 assert g['bench_front_feet_y']-g['ground_y']==(33 if i==0 else 0)
 legs=[v['rect'] for v in shapes if frames[i].contains(v['rect']) and abs(v['rect'].width-7)<1e-4 and abs(v['rect'].height-37)<1e-4]
 assert len(legs)==2
 for leg in legs:assert abs(leg.y1-(540-oy-g['bench_front_feet_y']))<1e-4
im=Image.open(png);im.verify();im=Image.open(png);assert im.size==(1800,1279) and im.mode=='RGB'
q={'title':'옮기는 동안','pages':1,'panels':4,'pdf_size_points':[760,540],'png_size':list(im.size),'wordless_pdf':True,'all_drawing_paths_within_panels':True,'both_character_colors_present_in_each_panel':True,'bench_seat_width_constant_points':130,'actual_pdf_front_leg_ground_contacts_verified':True,'first_panel_bench_lift_points':33,'visual_review':'Pending final inspection.','limits':['Static graphic continuity and clarity reviewed; no motion animation or physical load simulation.','Interpretive readings are qualitative reviews, not a human audience study.'],'hashes':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [pdf,png]}}
(P/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False,indent=2))
